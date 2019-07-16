import os
import pickle
import datetime
from time import sleep

import pandas as pd
import numpy as np

from WikiWho.utils import iter_rev_tokens
from wikiwho import open_pickle

from .wiki import Wiki
from .revision import Revision
from .utils import Timer


class Chobjer:

    def __init__(self, article, pickles_path, lang, context):
        self.ww_pickle = open_pickle(article, pickle_path=pickles_path, lang=lang)
        self.article = article
        self.context = context

    def get_revisions(self):
        revisions = self.ww_pickle.revisions
        return pd.DataFrame.from_records(((rev_id, Revision(rev_id, revisions[rev_id].timestamp,
                                                            revisions[rev_id].editor)) for rev_id in self.ww_pickle.ordered_revisions),
                                         columns=['id', ''], index='id').iloc[:, 0]

    def get_revisions_dict(self):
        revisions = self.ww_pickle.revisions
        return {rev_id: Revision(
            rev_id,
            datetime.datetime.strptime(
                revisions[rev_id].timestamp, r'%Y-%m-%dT%H:%M:%SZ'),
            # revisions[rev_id].timestamp,
            revisions[rev_id].editor) for rev_id in self.ww_pickle.ordered_revisions}

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

    def get_rev_content(self, rev_id):
        # from .utils import Timer
        # print('x')
        # with Timer():
        #     tokens = np.array([i for i in self.__get_token_ids(rev_id)])
        #     values = np.array([i for i in self.__get_values(rev_id)])
        # with Timer():
        #     df = pd.DataFrame(self.__iter_rev_content(rev_id), columns=['str', 'token_id'])

         return pd.DataFrame(self.__iter_rev_content(rev_id), columns=['str', 'token_id'])

    def create(self):

        revs = self.get_revisions_dict()
        revs_iter = iter(revs.items())
        from_rev_id, first_rev = next(revs_iter)

        first_rev.tokens = np.array([i for i in self.__get_token_ids(from_rev_id)])
        first_rev.values  = np.array([i for i in self.__get_values(from_rev_id)])

        #first_rev.content = self.get_rev_content(from_rev_id)

        # Getting first revision object and adding content ot it
        self.wiki = Wiki(self.article, revs, self.ww_pickle.tokens)

        # adding content to all other revision and finding change object
        # between them.
        for to_rev_id, _ in revs_iter:
            # for i, to_rev_id in enumerate(list(revs.index[1:])):
            #to_rev_content = self.get_rev_content(to_rev_id)

            from_rev = self.wiki.revisions[from_rev_id]
            to_rev = self.wiki.revisions[to_rev_id]

            to_rev.from_id = from_rev.id
            from_rev.to_id = to_rev.id

            to_rev.tokens = np.array([i for i in self.__get_token_ids(to_rev_id)])
            to_rev.values  = np.array([i for i in self.__get_values(to_rev_id)])

            self.wiki.create_change(from_rev, to_rev, self.context)
            from_rev_id = to_rev_id

    def iter_chobjs(self):

        revs = self.get_revisions_dict()
        revs_iter = iter(revs.items())
        from_rev_id, first_rev = next(revs_iter)
        first_rev.from_id = None

        first_rev.tokens = np.array([i for i in self.__get_token_ids(from_rev_id)])
        first_rev.values  = np.array([i for i in self.__get_values(from_rev_id)])
        #first_rev.content = self.get_rev_content(from_rev_id)

        # Getting first revision object and adding content ot it
        self.wiki = Wiki(self.article, revs, self.ww_pickle.tokens)

        # adding content to all other revision and finding change object
        # between them.
        for to_rev_id, _ in revs_iter:
            from_rev = self.wiki.revisions[from_rev_id]
            to_rev = self.wiki.revisions[to_rev_id]

            to_rev.from_id = from_rev.id
            from_rev.to_id = to_rev.id

            to_rev.tokens = np.array([i for i in self.__get_token_ids(to_rev_id)])
            to_rev.values  = np.array([i for i in self.__get_values(to_rev_id)])

            # for i, to_rev_id in enumerate(list(revs.index[1:])):
            #to_rev_content = self.get_rev_content(to_rev_id)
            for chobj in self.wiki.get_chobjs(from_rev, to_rev, self.context):
                yield chobj

            from_rev_id = to_rev_id




    def save(self, save_dir):
        save_filepath = os.path.join(
            save_dir, f"{self.article}_change.pkl")
        with open(save_filepath, "wb") as file:
            pickle.dump(self.wiki, file)

    def save_hd5(self, save_dir):

        revisions = self.wiki.revisions
        revisions = pd.Series(data=revisions, index=(
            r.id for r in revisions.values()))

        change_objects = [
            x.change_df for x in revisions if hasattr(x, 'change_df')]

        timestamp_s = pd.to_datetime(
            [rev.timestamp for rev in revisions.values.ravel().tolist()])

        time_gap = pd.to_timedelta(timestamp_s[1:] - timestamp_s[:-1])

        rev_ids = [rev.id for rev in revisions.tolist()]
        from_rev_ids = rev_ids[:-1]
        to_rev_ids = rev_ids[1:]

        editor_s = [rev.editor for rev in revisions.tolist()]

        index = list(zip(*[from_rev_ids, to_rev_ids,
                           timestamp_s.tolist()[1:], time_gap, editor_s[1:]]))
        change_df = pd.concat(change_objects, sort=False, keys=index, names=[
                              "from revision id", "to revision id", "timestamp", "timegap", "editor"])

        change_dataframe_path = os.path.join(
            save_dir, f"{self.article}_change.h5")
        change_df.to_hdf(change_dataframe_path, key="data", mode='w')
