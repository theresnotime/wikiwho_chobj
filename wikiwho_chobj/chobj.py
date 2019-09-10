import os
import pickle
import datetime
from time import sleep

import numpy as np

from WikiWho.utils import iter_rev_tokens
from wikiwho import open_pickle

from .revision import Revision
from .utils import Timer


class Chobjer:

    def __init__(self, article, pickles_path, lang, context):
        self.ww_pickle = open_pickle(
            article, pickle_path=pickles_path, lang=lang)
        self.article = article
        self.context = context

    def get_revisions_dict(self):
        revisions = self.ww_pickle.revisions
        return {
            rev_id: Revision(
                rev_id,
                datetime.datetime.strptime(
                    revisions[rev_id].timestamp, r'%Y-%m-%dT%H:%M:%SZ'),
                # revisions[rev_id].timestamp,
                revisions[rev_id].editor) for rev_id in self.ww_pickle.ordered_revisions
        }

    def get_one_revision(self, rev_id):
        revisions = self.ww_pickle.revisions
        return Revision(
                rev_id,
                datetime.datetime.strptime(
                    revisions[rev_id].timestamp, r'%Y-%m-%dT%H:%M:%SZ'),
                revisions[rev_id].editor)

    
    def __iter_rev_content(self, rev_id):
        yield ('{st@rt}', -1)
        for word in iter_rev_tokens(self.ww_pickle.revisions[rev_id]):
            yield (word.value, word.token_id)
        yield ('{$nd}', -2)

    def __get_token_ids(self, rev_id):
        yield -1
        for word in iter_rev_tokens(self.ww_pickle.revisions[rev_id]):
            yield word.token_id
        yield -2

    def __get_values(self, rev_id):
        yield '{st@rt}'
        for word in iter_rev_tokens(self.ww_pickle.revisions[rev_id]):
            yield word.value
        yield '{$nd}'

    def add_all_token(self, revisions, tokens):
        for token in tokens:
            # token.str
            revisions[token.origin_rev_id].added.append(token.token_id)
            for in_revision in token.inbound:
                revisions[in_revision].added.append(token.token_id)
            for out_revision in token.outbound:
                revisions[out_revision].removed.append(token.token_id)

    def iter_chobjs(self):

        # get all the revisions
        revs = self.get_revisions_dict()
        revs_iter = iter(revs.items())

        # prepare the first revision
        from_rev_id, first_rev = next(revs_iter)
        first_rev.from_id = None
        first_rev.tokens = np.array(
            [i for i in self.__get_token_ids(from_rev_id)])
        first_rev.values = np.array(
            [i for i in self.__get_values(from_rev_id)])

        # Getting first revision object and adding content ot it
        self.add_all_token(revs, self.ww_pickle.tokens)

        # adding content to all other revision and finding change object
        # between them.
        for to_rev_id, _ in revs_iter:

            # the two revisions that will be compare
            from_rev = revs[from_rev_id]
            to_rev = revs[to_rev_id]

            # make the revisions aware from the others ids
            to_rev.from_id = from_rev.id
            from_rev.to_id = to_rev.id

            # prepare the the next revisions
            to_rev.tokens = np.array(
                [i for i in self.__get_token_ids(to_rev_id)])
            to_rev.values = np.array([i for i in self.__get_values(to_rev_id)])

            # complete the next revision
            to_rev.inserted_continuous_pos()
            for chobj in from_rev.iter_chobs(self.article, to_rev, self.context):
                yield chobj

            # the to revision becomes the from revision
            from_rev_id = to_rev_id

        self.revs = revs

    def save(self, save_dir):
        save_filepath = os.path.join(
            save_dir, f"{self.article}_change.pkl")
        with open(save_filepath, "wb") as file:
            pickle.dump(self.wiki, file)
