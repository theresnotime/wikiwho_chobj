
from WikiWho.utils import iter_rev_tokens
from wikiwho import open_pickle
from WikiWho.utils import iter_rev_tokens

from Bio import pairwise2
from Bio.pairwise2 import format_alignment

from .timer import Timer


class GeneratorLen(object):

    def __init__(self, gen, length):
        self.gen = gen
        self.length = length

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.gen


class Chober:

    def __init__(self, article, pickles_path, lang, context):
        self.p = open_pickle(article, pickle_path=pickles_path, lang=lang)
        self.zip = 0
        self.nonzip = 0

    def get_chobs(self, r1, r2):
        r1 = self.p.ordered_revisions[r1]
        r2 = self.p.ordered_revisions[r2]

        self.__get_chobs(r1, r2)

    def __get_chobs(self, r1, r2):

        r1 = self.p.revisions[r1]
        r2 = self.p.revisions[r2]

        i1 = list(x.token_id for x in iter_rev_tokens(r1))
        i2 = list(x.token_id for x in iter_rev_tokens(r2))



        alignments = pairwise2.align.localxx(i1, i2, gap_char=["-"])

        for a in alignments:
            #print(a)
            print(format_alignment(*a))


    def get_dummy_chobs(self):



        X = 'abcxyzdefgwtur'
        Y = 'abcdefgvtu123r'

        alignments = pairwise2.align.globalxx(X, Y)


        # Use format_alignment method to format the alignments in the list
        for a in alignments:

            #print(a)
            print(format_alignment(*a))

        # s1 = 'abcxyzdefgwtur'
        # s2 = 'abcdefgvtu123r'
        # _s = SequenceMatcher(None, s1, s2)



        # for x in _s.get_opcodes():
        #     if x[0][0] != 'e':
        #         print('---')
        #         print('left: ' + s1[max(0, x[1] - 5):x[1]])
        #         print('dels: ' + s1[x[1]:x[2]])
        #         print('ins: ' + s2[x[3]:x[4]])
        #         print('right: ' + s1[x[2]:x[2] + 5])
