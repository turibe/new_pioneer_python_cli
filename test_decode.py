import unittest

import decoders

class TestDecode(unittest.TestCase):

    def test_basic(self):
        s = "FL022020204150504C45545620202020"
        r = decoders.decode_fl(s)
        self.assertEqual(r, "   APPLETV    ")

if __name__ == '__main__':
    unittest.main()
