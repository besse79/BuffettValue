import unittest
from buffettvalue.valuation import dcf

class DCFTest(unittest.TestCase):
 def test_value_and_no_trade(self):
  result=dcf(100,0.03,0.10,0.02,10,200,100,10)
  self.assertTrue(result['intrinsic_per_share']>0)
  self.assertFalse(result['paper_eligible'])
 def test_terminal_growth_cannot_exceed_discount(self):
  with self.assertRaises(ValueError): dcf(100,0.03,0.05,0.05,10,200,100,10)

 def test_invalid_horizon(self):
  for years in (True, 2.5, 0, 16):
   with self.subTest(years=years), self.assertRaises(ValueError):
    dcf(100,0.03,0.10,0.02,years,200,100,10)
 def test_invalid_terminal_growth(self):
  for growth in (-1,-1.1):
   with self.assertRaises(ValueError): dcf(100,0.03,0.10,growth,10,200,100,10)
 def test_boolean_financial_input(self):
  with self.assertRaises(ValueError): dcf(True,0.03,0.10,0.02,10,200,100,10)
