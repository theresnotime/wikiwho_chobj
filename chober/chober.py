
from WikiWho.utils import iter_rev_tokens
from wikiwho import open_pickle
from WikiWho.utils import iter_rev_tokens

from difflib import Differ
from .sequencematcher import SequenceMatcher

from .timer import Timer
import numpy as np

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

        i1 = list(iter_rev_tokens(self.p.revisions[r1]))
        i2 = list(iter_rev_tokens(self.p.revisions[r2]))

        _s = SequenceMatcher(None, i1, i2)

        for x in _s.get_opcodes():
            if x[0][0] != 'e':
                print('---')

                print(
                    'left: ' + ','.join(t.value for t in i1[max(0, x[1] - 5):x[1]]))
                print('dels: ' + ','.join(t.value for t in i1[x[1]:x[2]]))
                print('ins: ' + ','.join(t.value for t in i2[x[3]:x[4]]))
                print('right: ' + ','.join(t.value for t in i1[x[2]:x[2] + 5]))

    def __get_chobs(self, r1, r2):

        i1 = list(iter_rev_tokens(self.p.revisions[r1]))
        i2 = list(iter_rev_tokens(self.p.revisions[r2]))

        _s = SequenceMatcher(None, i1, i2)

        for x in _s.get_opcodes():
            if x[0][0] != 'e':
                print('---')

                print(
                    'left: ' + ','.join(t.value for t in i1[max(0, x[1] - 5):x[1]]))
                print('dels: ' + ','.join(t.value for t in i1[x[1]:x[2]]))
                print('ins: ' + ','.join(t.value for t in i2[x[3]:x[4]]))
                print('right: ' + ','.join(t.value for t in i1[x[2]:x[2] + 5]))

    def get_chobs_iter(self, r1, r2):
        r1 = self.p.ordered_revisions[r1]
        r2 = self.p.ordered_revisions[r2]
        return self._get_chobs_iter(r1,r2)


    def _get_chobs_iter(self, r1, r2):

        r1 = self.p.revisions[r1]
        r2 = self.p.revisions[r2]

        l1 = list(iter_rev_tokens(r1))
        l2 = list(iter_rev_tokens(r2))

        with Timer() as t2:
            lids1 = [i.token_id for i in iter_rev_tokens(r1)]
            lstr1 = [i.value for i in iter_rev_tokens(r1)]
            lids2 = [i.token_id for i in iter_rev_tokens(r2)]
            lstr2 = [i.value for i in iter_rev_tokens(r2)]

        with Timer() as t1:
            lids1, lstr1 = zip(*((i.token_id, i.value)
                                 for i in iter_rev_tokens(r1)))
            lids2, lstr2 = zip(*((i.token_id, i.value)
                                 for i in iter_rev_tokens(r2)))

        if t1.diff < t2.diff:
            self.zip += 1
        else:
            self.nonzip += 1


        for x in SequenceMatcher(None, lids1, lids2).get_opcodes():

            yield {
                'page_id': self.p.page_id,
                'from_rev': r1.id,
                'to_rev': r2.id,
                'from_timestamp': r1.timestamp,
                'to_timestamp': r1.timestamp,
                'editor': r1.editor,
                'ins_start_pos': x[1],
                'ins_end_pos': x[2],
                'left_neigh': lstr1[x[1]],
                'right_neigh': lstr1[x[2]-1],
                'del_start_pos': x[3],
                'del_end_pos': x[4],
                'left_tokens': lids1[max(0, x[1] - 5):x[1]],
                'del_tokens': lids1[x[1]:x[2]],
                'ins_tokens': lids2[x[3]:x[4]],
                'right_tokens': lids1[x[2]:x[2] + 5],
                'left_token_str': lstr1[max(0, x[1] - 5):x[1]],
                'del_tokens_str': lstr1[x[1]:x[2]],
                'ins_tokens_str': lstr2[x[3]:x[4]],
                'right_token_str': lstr1[x[2]:x[2] + 5],
                'text': (lstr1[max(0, x[1] - 5):x[1]],
                         lstr1[x[1]:x[2]],
                         lstr2[x[3]:x[4]],
                         lstr1[x[2]:x[2] + 5])
            }


    def get_all_chobs(self):
        for r1, r2 in zip(self.p.ordered_revisions, self.p.ordered_revisions[1:]):
            self.__get_chobs(r1, r2)

    def get_all_chobs_iter(self):
        r0 = self.p.revisions[self.p.ordered_revisions[0]]
        r0.lids = [i.token_id for i in iter_rev_tokens(r0)]
        r0.lstr = [i.value for i in iter_rev_tokens(r0)]

        for r1, r2 in zip(self.p.ordered_revisions, self.p.ordered_revisions[1:]):
            r1 = self.p.revisions[r1]
            r2 = self.p.revisions[r2]

            # with Timer() as t2:
            #     lids1 = [i.token_id for i in iter_rev_tokens(r1)]
            #     lstr1 = [i.value for i in iter_rev_tokens(r1)]
            #     lids2 = [i.token_id for i in iter_rev_tokens(r2)]
            #     lstr2 = [i.value for i in iter_rev_tokens(r2)]

            # with Timer() as t1:
            #     lids1, lstr1 = zip(*((i.token_id, i.value)
            #                          for i in iter_rev_tokens(r1)))
            #     lids2, lstr2 = zip(*((i.token_id, i.value)
            #                          for i in iter_rev_tokens(r2)))

            # if t1.diff < t2.diff:
            #     self.zip += 1
            # else:
            #     self.nonzip += 1


            lids1 = r1.lids
            lstr1 = r1.lstr

            lids2 = r2.lids = [i.token_id for i in iter_rev_tokens(r2)]
            lstr2 = r2.lstr = [i.value for i in iter_rev_tokens(r2)]

            # lids2 = [i.token_id for i in iter_rev_tokens(r2)]
            # lstr2 = [i.value for i in iter_rev_tokens(r2)]



            for op in SequenceMatcher(None, lids1, lids2).get_opcodes():
                yield {
                    'page_id': self.p.page_id,
                    'from_rev': r1.id,
                    'to_rev': r2.id,
                    'from_timestamp': r1.timestamp,
                    'to_timestamp': r1.timestamp,
                    'editor': r2.editor,
                    'ins_start_pos': op[0],
                    'ins_end_pos': op[1],
                    'left_neigh': lstr1[op[0]] if op[0] != op[1] else '' ,
                    'right_neigh': lstr1[op[1]-1] if op[0] != op[1] else '',
                    'del_start_pos': op[2],
                    'del_end_pos': op[3],
                    'left_tokens': lids1[max(0, op[0] - 5):op[0]],
                    'del_tokens': lids1[op[0]:op[1]],
                    'ins_tokens': lids2[op[2]:op[3]],
                    'right_tokens': lids1[op[1]:op[1] + 5],
                    'left_token_str': lstr1[max(0, op[0] - 5):op[0]],
                    'del_tokens_str': lstr1[op[0]:op[1]],
                    'ins_tokens_str': lstr2[op[2]:op[3]],
                    'right_token_str': lstr1[op[1]:op[1] + 5],
                    'text': (lstr1[max(0, op[0] - 5):op[0]],
                             lstr1[op[0]:op[1]],
                             lstr2[op[2]:op[3]],
                             lstr1[op[1]:op[1] + 5])
                }



    def get_dummy_chobs(self):

        s1 = 'abcxyzdefgwtur'
        s2 = 'abcdefgvtu123r'
        _s = SequenceMatcher(None, s1, s2)

        for x in _s.get_opcodes():
            if x[0][0] != 'e':
                print('---')
                print('left: ' + s1[max(0, x[1] - 5):x[1]])
                print('dels: ' + s1[x[1]:x[2]])
                print('ins: ' + s2[x[3]:x[4]])
                print('right: ' + s1[x[2]:x[2] + 5])
