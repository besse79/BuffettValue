import unittest
from buffettvalue.valuation import dcf

class DCFTest(unittest.TestCase):
 def test_value_and_no_trade(self):
  result=dcf(100,0.03,0.10,0.02,10,200,100,10)
  self.assertTrue(result['intrinsic_per_share']>0)
  self.assertFalse(result['paper_eligible'])
 def test_terminal_growth_cannot_exceed_discount(self):
  with self.assertRaises(ValueError): dcf(100,0.03,0.05,0.05,10,200,100,10)
