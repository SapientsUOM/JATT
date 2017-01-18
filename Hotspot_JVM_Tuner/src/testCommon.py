import unittest
import common as cmn

class TestCommon(unittest.TestCase):
    
    def test_get_max(self):
        val = 10
        max_val = cmn.get_max(val)
        self.assertEqual(15, max_val, "Max Value should be 15")
        
    def test_get_max_negative(self):
        val = -10
        max_val = cmn.get_max(val)
        self.assertEqual(-5, max_val, "Max Value should be -5 not -15")
        
    def test_get_min(self):
        val = 10
        min_val = cmn.get_min(val)
        self.assertEqual(5, min_val, "min vlaue should be 5")
        
    def test_get_min_negative(self):
        val = -10
        min_val = cmn.get_min(val)
        self.assertEqual(-15, min_val, "min vlaue should be -15 not -5")
    
    def test_is_float_true(self):
        val = 10.00
        return_val = cmn.isfloat(val)
        self.assertEqual(True, return_val)
        
    def test_is_float_false(self):
        val = "ab"
        return_val = cmn.isfloat(val)
        self.assertEqual(False, return_val)
        
if __name__ == '__main__':
    unittest.main()
