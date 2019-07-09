
from WikiWho.utils import iter_rev_tokens
from wikiwho import open_pickle
from WikiWho.utils import iter_rev_tokens

from difflib import Differ
from difflib import SequenceMatcher



class Chober:

    def __init__(self, article, pickles_path, lang, context):
        self.p = open_pickle(article, pickle_path=pickles_path, lang=lang)
        self.d = Differ()


    def get_chobs(self, r1, r2):
        r1 = self.p.ordered_revisions[r1]
        r2 = self.p.ordered_revisions[r2]

        i1 = list(iter_rev_tokens(self.p.revisions[r1]))
        i2 = list(iter_rev_tokens(self.p.revisions[r2]))

        _s = SequenceMatcher(None, i1, i2)


        for x in _s.get_opcodes():
            if x[0][0] != 'e':
                print('---')
                print('ins: ' + ','.join( t.value for t in i1[x[1]:x[2]]) )
                print('dels: ' + ','.join( t.value for t in i2[x[3]:x[4]]) )



    def get_dummy_chobs(self):

        s1 = 'abcxyzdefgwtu'
        s2 = 'abcdefgvtu123'
        _s = SequenceMatcher(None, s1, s2) 


        for x in _s.get_opcodes():
            if x[0][0] != 'e':
                print('---')
                print('ins: ' + s1[x[1]:x[2]])
                print('dels: ' + s2[x[3]:x[4]])






