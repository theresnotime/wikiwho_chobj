import os
import pickle
from time import sleep

import pandas as pd

from .wiki import Wiki
from .revision import Revision

class Chobjer:

    def __init__(self, wikiwho, article_name, epsilon_size):
        self.ww = wikiwho
        self.article_name = article_name
        self.epsilon_size = epsilon_size

    def df_rev_content(self, rev_id, first=False):
        rev_content = self.ww.api.specific_rev_content_by_rev_id(
            rev_id, self.article_name,  o_rev_id=False, editor=False, _in=False, out=False
            )["revisions"][0]
        _, rev_content = next(iter(rev_content.items()))
        rev_content = rev_content['tokens']
        rev_content.insert(0, {'str': '{st@rt}', 'token_id': -1})
        rev_content.append({'str': '{$nd}', 'token_id': -2})
        rev_content = pd.DataFrame(rev_content)
        return rev_content

    def create(self):

        rev_list = pd.DataFrame(self.ww.api.rev_ids_of_article(
            self.article_name)["revisions"])
        all_tokens = self.ww.api.all_content(
            self.article_name, editor=False)["all_tokens"]

        # making revision objects
        revs = rev_list.apply(lambda rev: Revision(
            rev["id"], rev["timestamp"], rev["editor"]), axis=1)
        revs.index = rev_list.id

        # Getting first revision object and adding content ot it
        from_rev_id = revs.index[0]
        self.wiki = Wiki(self.article_name, revs, all_tokens)

        self.wiki.revisions.iloc[0].content = self.df_rev_content(
            from_rev_id, first=True)
        # adding content to all other revision and finding change object
        # between them.

        for i, to_rev_id in enumerate(list(revs.index[1:])):
            to_rev_content = self.df_rev_content(to_rev_id)
            self.wiki.create_change(
                from_rev_id, to_rev_id, to_rev_content, self.epsilon_size)
            from_rev_id = to_rev_id
            print(i)

    def save(self, save_dir):
        save_filepath = os.path.join(
            save_dir, f"{self.article_name}_change.pkl")
        with open(save_filepath, "wb") as file:
            pickle.dump(self.wiki, file)

    def save_hd5(self, save_dir):

        change_objects = []
        self.wiki.revisions.iloc[
            :-1].apply(lambda revision: change_objects.append(revision.change_df))

        timestamp_s = pd.to_datetime(
            [rev.timestamp for rev in self.wiki.revisions.values.ravel().tolist()])
        time_gap = pd.to_timedelta(timestamp_s[1:] - timestamp_s[:-1])

        rev_ids = [rev.id for rev in self.wiki.revisions.tolist()]
        from_rev_ids = rev_ids[:-1]
        to_rev_ids = rev_ids[1:]

        editor_s = [rev.editor for rev in self.wiki.revisions.tolist()]

        index = list(zip(*[from_rev_ids, to_rev_ids,
                           timestamp_s.tolist()[1:], time_gap, editor_s[1:]]))
        change_df = pd.concat(change_objects, sort=False, keys=index, names=[
                              "from revision id", "to revision id", "timestamp", "timegap", "editor"])

        change_dataframe_path = os.path.join(
            save_dir, f"{self.article_name}_change.h5")
        change_df.to_hdf(change_dataframe_path, key="data", mode='w')


