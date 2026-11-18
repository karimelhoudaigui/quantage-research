"""Bounded software fixtures only; no C23 corpus, gold, model, socket or GPU."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

from quantage import repair_scale_full_inference as full
from quantage import repair_study_c23 as study
from quantage.repair_language import parse_proposal
from quantage.repair_model import verify_model
from quantage.repair_patch_tool_language import parse_patch
from quantage.repair_trace_feedback import build_feedback


class C23SoftwareFixtures(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root=Path(temporary.name)
        self.case={'id':'software-c23-fixture','language':'fr','intention':'SYNTHETIC exclusion fixture.',
                   'data':{'n':2,'weights':[3,2],'costs':[1,1],'edges':[[0,1]]}}
        self.spec={'budget':None,'min_count':None,'max_count':None,'required':[],'forbidden':[],'implications':[]}
        self.bad={'formulation':'binary_ilp','variables':[0,1],'sense':'max','objective':[3,2],
                  'constraints':['x0+x1<=2']}
        self.good={**self.bad,'constraints':['x0+x1<=1']}
        self.initial_raw=json.dumps(self.bad)
        self.public={self.case['id']:self.case}

    def write_rows(self,path,rows):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(''.join(json.dumps(row,allow_nan=False)+'\n' for row in rows))

    def record(self,phase,raw,trace=None):
        messages=[{'role':'system','content':'FULL FIXTURE' if phase in ('initial','direct') else 'PATCH FIXTURE'},
                  {'role':'user','content':json.dumps({'intention':self.case['intention'],'data':self.case['data']})}]
        patch_phase=phase in ('self','guided')
        if patch_phase:
            messages.append({'role':'assistant','content':self.initial_raw})
            follow=study.SELF_INSTRUCTION if phase=='self' else json.dumps({
                'verifier_feedback':trace['verdict'],'candidate_evaluation_tool':trace['candidate_evaluations'],
                'gloss':trace['gloss'],'instruction':study.GUIDED_INSTRUCTION})
            messages.append({'role':'user','content':follow})
        logs=[-.1,-.1] if phase=='direct' else [-.5,-.125]
        row={'id':self.case['id'],'phase':phase,'seed':full.seed_for(self.case['id'],phase),
             'messages':messages,'raw_response':raw,
             'parsed':parse_patch(raw,2,self.initial_raw) if patch_phase else parse_proposal(raw,2),
             'input_tokens':10,'input_token_ids':list(range(10)),
             'output_tokens':2,'generated_token_ids':[101,151645],
             'generated_token_log_probabilities':logs,'mean_generated_log_probability':sum(logs)/len(logs),
             'finish_reason':'eos','wall_seconds':.01,'cpu_seconds':.001}
        if patch_phase:
            row['initial_response_sha256']=hashlib.sha256(self.initial_raw.encode()).hexdigest()
        return row

    def test_raw_patch_replay_repairs_an_initial_that_has_no_valid_full_parse(self):
        invalid={**self.bad,'variables':[0]}
        self.initial_raw=json.dumps(invalid)
        first=self.record('initial',self.initial_raw)
        self.assertFalse(first['parsed']['valid'])
        patch=json.dumps({'diagnosis':'Variable arity is wrong.','edits':[{'op':'set_variables','values':[0,1]}]})
        row=self.record('self',patch)
        self.assertTrue(row['parsed']['valid'],row['parsed'])
        path=self.root/'self.jsonl';self.write_rows(path,[row])
        loaded=study.indexed(path,self.public,'self',initial={self.case['id']:first})
        self.assertEqual(loaded[self.case['id']]['parsed']['authored_model']['variables'],[0,1])
        self.assertEqual(loaded[self.case['id']]['parsed']['authored_patch']['edits'][0]['op'],'set_variables')
        row['messages'][2]['content']=self.initial_raw+' '
        self.write_rows(self.root/'wrong.jsonl',[row])
        with self.assertRaises(ValueError):
            study.indexed(self.root/'wrong.jsonl',self.public,'self',initial={self.case['id']:first})

    def test_complete_fixture_feedback_patch_models_portfolios_and_cost_accounting(self):
        cases=self.root/'cases.json';gold=self.root/'gold.json'
        cases.write_text(json.dumps([self.case]))
        gold.write_text(json.dumps([{'id':self.case['id'],'constraints':self.spec,'families':[]}]))
        paths={name:self.root/name/'raw.jsonl' for name in ('initial','direct','self','guided')}
        first=self.record('initial',self.initial_raw)
        self.write_rows(paths['initial'],[first])
        study.feedback(cases,gold,paths['initial'],self.root/'feedback')
        trace=json.loads((self.root/'feedback/minimal.json').read_text())[self.case['id']]
        self.assertEqual(set(trace),{'verdict','candidate_evaluations','gloss'})
        self.assertEqual(trace['candidate_evaluations'][0]['rows'][0]['rhs'],2)
        self.write_rows(paths['direct'],[self.record('direct',json.dumps(self.good))])
        self.write_rows(paths['self'],[self.record('self',json.dumps({'diagnosis':'No change.','edits':[]}))])
        repair=json.dumps({'diagnosis':'The joint selection must be excluded.',
                           'edits':[{'op':'replace_constraint','index':0,'row':'x0+x1<=1'}]})
        self.write_rows(paths['guided'],[self.record('guided',repair,trace)])
        study.score(cases,gold,paths['initial'],paths['direct'],paths['self'],paths['guided'],
                    self.root/'scores',self.root/'feedback/reports.jsonl')
        metrics=json.loads((self.root/'scores/metrics.json').read_text())
        results=json.loads((self.root/'scores/raw.jsonl').read_text())['results']
        self.assertEqual(metrics['physical_generation_calls'],4)
        self.assertEqual(metrics['planned_call_accounting'],{'physical':4,'attributable_across_three_arms':6})
        self.assertEqual(metrics['H23']['required_gain'],3)
        self.assertEqual(metrics['primary_comparison'],'guided_tool_patch versus self_patch')
        self.assertEqual(results['guided']['raw_patch'],repair)
        self.assertEqual(results['guided']['patch_materialized_authored_model'],self.good)
        self.assertTrue(results['guided']['usable_for_original_problem'])
        self.assertFalse(results['self']['usable_for_original_problem'])
        self.assertTrue(results['self']['portfolio']['concordance'])
        self.assertEqual(results['self']['portfolio']['objective'],5)
        self.assertEqual(results['guided']['portfolio']['objective'],3)

    def test_patch_fallback_preserves_raw_failed_attempt(self):
        first=self.record('initial',self.initial_raw)
        failed=self.record('self','not JSON')
        self.assertFalse(failed['parsed']['valid'])
        selected,index=study.choose_revision(first,failed)
        self.assertEqual(index,0)
        self.assertIs(selected,first)
        self.assertEqual(failed['raw_response'],'not JSON')

    def test_full_phase_is_independent_and_budget_reserve_is_1024(self):
        self.assertEqual(full.PHASES,('initial','direct'))
        self.assertEqual(full.MAX_NEW_TOKENS,1024)
        self.assertEqual(full.completion_request([1]*3071,123)['n_predict'],1024)
        with self.assertRaises(ValueError):full.completion_request([1]*3072,123)
        for phase in ('self','guided'):
            with self.assertRaises(ValueError):full.validate_phase_inputs(phase,None,None)
        with self.assertRaises(ValueError):full.validate_phase_inputs('direct',Path('never-read'),None)

    def test_full_driver_native_closed_thinking_guard_with_no_process_or_model(self):
        binary=self.root/'runtime/llama-b12359/llama-server';binary.parent.mkdir(parents=True)
        binary.write_bytes(b'SOFTWARE FIXTURE NOT EXECUTABLE')
        model=self.root/'fixture.gguf';model.write_bytes(b'GGUF SOFTWARE FIXTURE NO WEIGHTS')
        acquisition=self.root/'acquisition.json'
        acquisition.write_text(json.dumps({'status':'completed','runtime_tag':'b12359',
            'model':{'sha256_expected':full.digest(model)},
            'downloads':[{'destination':str(model),'status':'completed',
                          'sha256_expected':full.digest(model),'sha256_observed':full.digest(model)}],
            'runtime_extraction':{'files':[{'path':'llama-b12359/llama-server','sha256':full.digest(binary)}]}}))
        cases=self.root/'public.json';cases.write_text(json.dumps([self.case]))
        instructions=self.root/'instructions.txt';instructions.write_text('FULL FIXTURE')
        owner=self
        calls=[]
        class Client:
            last_response_bytes=None
            def request(self,endpoint,payload=None,timeout=None):
                if endpoint=='/apply-template':
                    return {'prompt':'<|im_start|>assistant\n'+owner.suffix}
                if endpoint=='/tokenize':return {'tokens':[1,2]}
                calls.append(payload)
                response={'content':json.dumps(owner.good),'tokens':[101,151645],
                    'completion_probabilities':[{'id':101,'prob':.5},{'id':151645,'prob':1.}],
                    'tokens_predicted':2,'tokens_evaluated':2,'truncated':False,'stop_type':'eos',
                    'generation_settings':{**{key:payload[key] for key in
                        ('seed','samplers','temperature','top_k','top_p','min_p','n_predict','post_sampling_probs')},
                        'speculative.types':'none','backend_sampling':False}}
                self.last_response_bytes=full.json_bytes(response)
                return response
        class Server:
            command=['SOFTWARE FIXTURE NO EXECUTION']
            stats={'injected_software_fixture':True,'server_cpu_seconds':0.}
            def __init__(self,*args):pass
            def start(self):return Client()
            def stop(self):pass
        with mock.patch.object(full.subprocess,'Popen',side_effect=AssertionError('no model execution allowed')), \
             mock.patch.object(full.shutil,'disk_usage',return_value=SimpleNamespace(free=10*1024**3)):
            self.suffix='<think>\n</think>\n\n'
            record=full.run_phase(cases_path=cases,instructions_path=instructions,phase='initial',
                output=self.root/'accepted',binary=binary,model=model,acquisition_path=acquisition,server_factory=Server)
            self.assertTrue(record['nonthinking_prompt_suffix_checked'])
            self.assertEqual(calls[0]['n_predict'],1024)
            for index,suffix in enumerate(('<think>\n','<think>hidden work</think>','')):
                self.suffix=suffix
                before=len(calls)
                with self.assertRaises(ValueError):
                    full.run_phase(cases_path=cases,instructions_path=instructions,phase='initial',
                        output=self.root/('rejected'+str(index)),binary=binary,model=model,
                        acquisition_path=acquisition,server_factory=Server)
                self.assertEqual(before,len(calls))


if __name__=='__main__':unittest.main()
