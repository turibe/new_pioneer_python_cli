import unittest

from sources import SourceMap

class TestSources(unittest.TestCase):

    def test_init(self):
        s = SourceMap()
        self.assertEqual(s.source_map["05"], "TV")
        self.assertEqual(s.inverse_map["tv"], "05FN")

    def test_aliases(self):
        s = SourceMap()
        val = s.inverse_map["tv"]
        s.add_alias("television", "TV")
        s.add_alias("tele", "television")
        self.assertEqual(s.inverse_map["television"], val)
        self.assertEqual(s.inverse_map["tele"], val)



if __name__ == '__main__':
    unittest.main()
