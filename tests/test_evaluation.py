"""Metric and missing-trace tests with explicit software fixtures, not LLM data."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from quantage.evaluation import index_rows, load_json, run
from quantage.benchmark import mis_request, photon_request
from test_agent_pipeline import fixture


class Evaluation(unittest.TestCase):
    def test_duplicate_or_missing_ids_rejected(self):
        with self.assertRaises(ValueError):index_rows([{'id':'x'},{'id':'x'}],['x'],'fixture')
        with self.assertRaises(ValueError):index_rows([],['x'],'fixture')

    def test_missing_traces_are_not_scored_as_abstentions(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);request=mis_request(1,[])
            (d/'public.json').write_text(json.dumps([{'id':'x','request':request}]))
            (d/'gold.json').write_text(json.dumps([{'id':'x','expected_action':'propose','family':'mis'}]))
            (d/'arms.json').write_text(json.dumps([{'name':'missing','files':[]}]))
            with contextlib.redirect_stdout(io.StringIO()):run(d/'public.json',d/'gold.json',d/'arms.json',d/'out')
            m=load_json(d/'out/metrics.json')
            self.assertEqual(m['agent_cases_evaluated'],0)
            self.assertNotIn('missing_schema',m['methods'])
            self.assertEqual(m['native_comparison_status'],'blocked')

    def test_counting_semantic_errors_separately_from_numeric(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);mis=mis_request(2,[[0,1]],[1,2]);photon=photon_request(.2,.3,.4)
            p=fixture(mis);p['id']='x';q=fixture(photon);q['id']='y'
            mis['intent']='Count all independent sets.'
            public=[{'id':'x','request':mis},{'id':'y','request':photon}]
            gold=[{'id':'x','expected_action':'abstain','family':'mis'},{'id':'y','expected_action':'propose','family':'photon'}]
            for name,content in [('public',public),('gold',gold),('responses',[p,q])]:
                (d/(name+'.json')).write_text(json.dumps(content))
            (d/'arms.json').write_text(json.dumps([{'name':'software_fixture','files':[str(d/'responses.json')]}]))
            with contextlib.redirect_stdout(io.StringIO()):run(d/'public.json',d/'gold.json',d/'arms.json',d/'out')
            m=load_json(d/'out/metrics.json')['methods']['software_fixture_verified']
            self.assertEqual(m['false_accept'],1)
            self.assertEqual(m['accepted_supported'],1)
            self.assertEqual(m['accepted_numeric_invalid'],0)


if __name__=='__main__':unittest.main()
