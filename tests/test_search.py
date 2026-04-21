import unittest
from cquarry.db import CalibreDB

class TestSearchParser(unittest.TestCase):
    def tokenize(self, expr):
        # We can use CalibreDB class itself as 'self' for _tokenize_vl
        # since it only calls @staticmethods _read_value and _read_word.
        return CalibreDB._tokenize_vl(CalibreDB, expr)
    
    def test_tokenize_basic_tags(self):
        tokens = self.tokenize('tags:Fic.Fantasy')
        self.assertEqual(tokens, ['tags:Fic.Fantasy'])
        
        tokens = self.tokenize('tags:"=Fic.Fantasy"')
        self.assertEqual(tokens, ['tags:=Fic.Fantasy'])

    def test_tokenize_authors(self):
        tokens = self.tokenize('author:Anne')
        self.assertEqual(tokens, ['authors:Anne'])
        
        tokens = self.tokenize('authors:"Anne Rice"')
        self.assertEqual(tokens, ['authors:Anne Rice'])

    def test_tokenize_unquoted_author(self):
        # Unquoted space acts as an implicit AND in standard Calibre,
        # so "author:Anne Rice" is parsed as author:Anne and a general search for Rice.
        tokens = self.tokenize('author:Anne Rice')
        self.assertEqual(tokens, ['authors:Anne', 'Rice'])

    def test_tokenize_boolean_operators(self):
        tokens = self.tokenize('tags:Fic AND NOT tags:Horror')
        self.assertEqual(tokens, ['tags:Fic', 'AND', 'NOT', 'tags:Horror'])

        tokens = self.tokenize('tags:Fic OR tags:NonFic')
        self.assertEqual(tokens, ['tags:Fic', 'OR', 'tags:NonFic'])

    def test_tokenize_grouping(self):
        tokens = self.tokenize('NOT(tags:Fic.Romance OR tags:Fic.Contemporary)')
        self.assertEqual(tokens, ['NOT', '(', 'tags:Fic.Romance', 'OR', 'tags:Fic.Contemporary', ')'])

        tokens = self.tokenize('(tags:Fic OR tags:NonFic) AND NOT tags:Gaming')
        self.assertEqual(tokens, ['(', 'tags:Fic', 'OR', 'tags:NonFic', ')', 'AND', 'NOT', 'tags:Gaming'])

    def test_tokenize_complex_calibre_parity(self):
        # tests:"Fic.Fantasy.Grimdark" AND author:"Phil Tucker"
        tokens = self.tokenize('tags:"Fic.Fantasy.Grimdark" AND author:"Phil Tucker"')
        self.assertEqual(tokens, ['tags:Fic.Fantasy.Grimdark', 'AND', 'authors:Phil Tucker'])

    def test_tokenize_implicit_and(self):
        tokens = self.tokenize('tags:Fic tags:Fantasy')
        self.assertEqual(tokens, ['tags:Fic', 'tags:Fantasy'])

if __name__ == '__main__':
    unittest.main()
