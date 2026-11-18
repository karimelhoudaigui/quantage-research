"""Semantic and adversarial tests of literal edits, without a language model."""
import itertools,json,unittest
from quantage.repair_patch_language import parse_patch

class LiteralEdits(unittest.TestCase):
 def setUp(self):
  self.base={'formulation':'binary_ilp','variables':[0,1,2],'sense':'max','objective':[5,4,3],'constraints':['x0+x1<=1']}
  self.raw=json.dumps(self.base)
 def apply(self,edits,diagnosis='Check clauses'):
  return parse_patch(json.dumps({'diagnosis':diagnosis,'edits':edits}),3,self.raw)
 def test_diagnosis_cannot_edit(self):
  p=self.apply([], 'Remove every constraint and set objective to zero')
  self.assertTrue(p['valid']);self.assertEqual(p['authored_model'],self.base)
 def test_literal_objective_not_autocorrected(self):
  p=self.apply([{'op':'set_objective','values':[99,-4,0]}])
  self.assertTrue(p['valid']);self.assertEqual(p['model']['objective'],[99,-4,0])
 def test_all_operations_and_current_indices(self):
  p=self.apply([{'op':'add_constraint','row':'x2==1'},{'op':'replace_constraint','index':0,'row':'x0+x1<=0'},{'op':'delete_constraint','index':0},{'op':'set_objective','values':[2,3,4]},{'op':'set_variables','values':[0,1,2]}])
  self.assertTrue(p['valid']);self.assertEqual(p['authored_model']['constraints'],['x2==1'])
  row=p['model']['constraints'][0];self.assertEqual(row,[[0,0,1],'==',1])
  for bits in itertools.product((0,1),repeat=3):
   self.assertEqual(sum(c*x for c,x in zip(row[0],bits))==row[2],bits[2]==1)
  replaced=parse_patch(json.dumps({'diagnosis':'All fields supplied','edits':[{'op':'replace_model','model':self.base}]}),3,'not JSON')
  self.assertTrue(replaced['valid']);self.assertEqual(replaced['authored_model'],self.base)
 def test_atomic_invalid_patch(self):
  p=self.apply([{'op':'add_constraint','row':'x2==1'},{'op':'delete_constraint','index':31}])
  self.assertFalse(p['valid']);self.assertNotIn('model',p);self.assertEqual(json.loads(self.raw),self.base)
 def test_wrong_variables_not_completed(self):
  for values in ([1,2,0],[0,1],[],[0,True,2]):self.assertFalse(self.apply([{'op':'set_variables','values':values}])['valid'])
 def test_authored_coefficients_preserved(self):
  p=self.apply([{'op':'replace_constraint','index':0,'row':'7*x0-3*x1+2*x2<=9'}])
  self.assertTrue(p['valid']);self.assertEqual(p['model']['constraints'],[[[7,-3,2],'<=',9]])
 def test_injection_duplicate_and_boolean_index_rejected(self):
  self.assertFalse(self.apply([{'op':'delete_constraint','index':True}])['valid'])
  self.assertFalse(self.apply([{'op':'add_constraint','row':'__import__("os").system("false")<=0'}])['valid'])
  self.assertFalse(parse_patch('{"diagnosis":"x","edits":[],"edits":[]}',3,self.raw)['valid'])
 def test_diagnosis_bounds_and_ascii(self):
  for text in ('x'*257,'repair\nrow','é'):self.assertFalse(self.apply([],text)['valid'])

if __name__=='__main__':unittest.main()
