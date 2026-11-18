"""Scoring tests use software fixtures only, with no inference or benchmark data."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from quantage.local_score import score
from quantage.compact_agent import parse_compact
from quantage.benchmark import mis_request,photon_request


class LocalScore(unittest.TestCase):
    def test_pairing_missing_and_semantic_numeric_separation(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);photon=photon_request(.2,.3,.4);photon['intent']='Compute complex single-photon amplitudes.'
            cases=[{'id':'fixture_x','request':mis_request(1,[])},{'id':'fixture_y','request':photon}]
            gold=[{'id':'fixture_x','expected_action':'propose','family':'mis'},
                  {'id':'fixture_y','expected_action':'abstain','family':'photon'}]
            def row(cid,arm,proposal):
                raw=json.dumps(proposal)
                return {'id':cid,'arm':arm,'raw_response':raw,'parsed':parse_compact(raw),
                        'input_tokens':10,'output_tokens':10,'wall_seconds':1.,'cpu_seconds':1.,'finish_reason':'eos'}
            records=[row('fixture_x','alone',{'action':'propose','family':'mis','task':'maximum_weight_independent_set','reason':'software fixture'}),
                     row('fixture_x','documented',{'action':'abstain','family':'mis','task':None,'reason':'software fixture'}),
                     row('fixture_y','documented',{'action':'propose','family':'photon','task':'ideal_single_photon_probabilities','reason':'software fixture'})]
            for name,value in [('cases',cases),('gold',gold)]: (d/(name+'.json')).write_text(json.dumps(value))
            (d/'responses.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records))
            with contextlib.redirect_stdout(io.StringIO()):score(d/'cases.json',d/'gold.json',d/'responses.jsonl',d/'out')
            result=json.loads((d/'out/metrics.json').read_text())
            self.assertEqual(result['missing_generation_records'],1)
            self.assertEqual(result['methods']['alone']['observed'],1)
            self.assertEqual(result['methods']['alone']['accepted_supported'],1)
            self.assertEqual(result['methods']['documented']['semantic_errors_with_numeric_certificate'],1)
            self.assertEqual(result['paired']['both_observed'],1)
            self.assertEqual(result['paired']['alone_only_correct_accept'],1)


if __name__=='__main__':unittest.main()
