from wiki import Wiki
from revision import Revision
from wikiwho_wrapper import WikiWho
import pandas as pd
from time import sleep
import pickle
import numpy as np
import traceback
import os


class ChangeObject:

    def __init__(self, article_name, epsilon_size):
        self.article_name = article_name
        self.epsilon_size = epsilon_size

    def create_change_object(self, article_name, content_dir="../data/content/",
                             change_object_dir="../data/change objects/", epsilon_size=30, save=False):

        content_filepath = os.path.join(content_dir, article_name + ".h5")
        change_object_filepath = os.path.join(
            change_object_dir, article_name + ".pkl")

        with pd.HDFStore(content_filepath, 'r') as store:
            # retrieving all rev list and change object from file
            rev_list = store.get("rev_list")
            all_rev = store.get("all_tokens")
            all_tokens = all_rev.to_dict(orient="records")

            # making revision objects
            revs = rev_list.apply(lambda rev: Revision(
                rev["id"], rev["timestamp"], rev["editor"]), axis=1)
            revs.index = rev_list.id

            # Getting first revision object and adding content ot it
            from_rev_id = revs.index[0]
            wiki = Wiki(article_name, revs, all_tokens)

            wiki.revisions.iloc[0].content = store["r" + str(from_rev_id)]
            # adding content to all other revision and finding change object
            # between them.

            for to_rev_id in list(revs.index[1:]):
                key = "r" + str(to_rev_id)
                to_rev_content = store[key]
                wiki.create_change(from_rev_id, to_rev_id,
                                   to_rev_content, epsilon_size)
                from_rev_id = to_rev_id

        if save:
            with open(change_object_filepath, "wb") as file:
                pickle.dump(wiki, file)

        return wiki

    def df_rev_content(self, key, first=False):
        rev_content = self.ww.api.specific_rev_content_by_rev_id(
            key, o_rev_id=False, editor=False, _in=False, out=False)["revisions"][0][str(key)]["tokens"]
        rev_content.insert(0, {'str': '{st@rt}', 'token_id': -1})
        rev_content.append({'str': '{$nd}', 'token_id': -2})
        rev_content = pd.DataFrame(rev_content)
        return rev_content

    def get_str_tokenid_for_rev(self, rev):
        strs = [tok["str"] for tok in self.ww.dv.api.specific_rev_content_by_rev_id(
            key)["revisions"][0][str(key)]["tokens"]]
        tokens = [tok["token_id"] for tok in self.ww.dv.api.specific_rev_content_by_rev_id(
            key)["revisions"][0][str(key)]["tokens"]]
        rev_len_list = pd.DataFrame({"str": strs, "token_id": tokens})
        rev_len_list = self.add_start_end_token(rev_len_list, add_false=False)
        return rev_len_list

    def create(self):
        self.ww = WikiWho(protocol="http", domain="10.6.13.139")

        r_ids = self.ww.api.rev_ids_of_article("Bioglass")
        rev_list = pd.DataFrame(r_ids["revisions"])
        all_rev = pd.DataFrame(
            self.ww.api.all_content("Bioglass")["all_tokens"])
        del all_rev["editor"]
        all_tokens = all_rev.to_dict(orient="records")

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
            # sleep(1)

    def save(self, save_dir):
        save_filepath = os.path.join(
            save_dir, self.article_name + "_change.pkl")
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
            save_dir, self.article_name + "_change.h5")
        change_df.to_hdf(change_dataframe_path, key="data", mode='w')


if __name__ == "__main__":
    epsilon_size = 30
    article_name = 'Bioglass'
    change_object_dir = "data/change objects/"
    co = ChangeObject(article_name, epsilon_size)
    co.create()
    co.save(change_object_dir)
    co.save_hd5(change_object_dir)
