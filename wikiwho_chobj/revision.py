import pandas as pd
import numpy as np

columns = ["ins_tokens", "del_tokens",
           "ins_tokens_str", "del_tokens_str",
           "left_neigh_slice", "right_neigh_slice",
           "left_token", "right_token",
           "left_token_str", "right_token_str"]


class Revision:

    def __init__(self, id, timestamp, editor):
        self.id = id
        self.timestamp = timestamp
        self.editor = editor
        self.added = list()
        self.removed = list()

    def deleted(self, to_rev):
        removed = np.isin(self.tokens,
                          to_rev.removed, assume_unique=True).astype(np.int)
        ediff = np.ediff1d(
            np.pad(removed, (1, 1), mode="constant", constant_values=0))

        start_pos = np.argwhere(ediff == 1)
        end_pos = np.argwhere(ediff == -1) - 1
        start_neighbour = start_pos - 1
        end_neighbour = end_pos + 1

        self.del_start_pos = np.nonzero(ediff == 1)[0]
        self.del_end_pos = np.nonzero(ediff == -1)[0] - 1
        self.del_start_neighbour = self.del_start_pos - 1
        self.del_end_neighbour = self.del_end_pos + 1

        self.deleted_object = pd.DataFrame(np.c_[start_pos, end_pos, start_neighbour, end_neighbour],
                                           columns=["del_start_pos", "del_end_pos", "left_neigh", "right_neigh", ])

    def inserted_continuous_pos(self):

        added = np.isin(self.tokens, self.added,
                        assume_unique=True).astype(np.int)

        ediff = np.ediff1d(
            np.pad(added, (1, 1), mode="constant", constant_values=0))

        start_pos = np.argwhere(ediff == 1)
        end_pos = np.argwhere(ediff == -1) - 1

        self.ins_start_pos = np.nonzero(ediff == 1)[0]
        self.ins_end_pos = np.nonzero(ediff == -1)[0] - 1

        self.added_pos = np.c_[start_pos, end_pos]

    def inserted_neighbours(self):
        start_token_pos = self.added_pos[:, 0] - 1
        end_token_pos = self.added_pos[:, 1] + 1
        self.start_token_id = self.tokens[start_token_pos]
        self.end_token_id = self.tokens[end_token_pos]

    def create_change_object(self, to_rev):
        self.ins_left = np.argwhere(
            np.isin(self.tokens, to_rev.start_token_id, assume_unique=True))
        self.ins_right = np.argwhere(
            np.isin(self.tokens, to_rev.end_token_id, assume_unique=True))

        self.ins_left_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.start_token_id, assume_unique=True))[0]
        self.ins_right_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.end_token_id, assume_unique=True))[0]

        self.inserted_object = pd.DataFrame(np.concatenate([to_rev.added_pos, self.ins_left, self.ins_right], axis=1),
                                            columns=["ins_start_pos", "ins_end_pos", "left_neigh", "right_neigh"])

        self.change = pd.merge(self.inserted_object, self.deleted_object, how="outer", on=[
                               "left_neigh", "right_neigh"])


        # asdf = []
        # for isp, iep, iln, irn in zip(*self.inserted_object.values.transpose()):
        #     for dsp, dep, dln, drn in zip(*self.deleted_object.values.transpose()):
        #         asdf.append('')


        # if len(self.change) > 2 and len(self.change) < 10:
        #     if not (np.diff(self.inserted_object['left_neigh']) > 0).all():
        #         print('err')

        #     didx = 0

        ####################################################

        # self.ins_start_pos
        # self.ins_end_pos
        # self.ins_left_neigh
        # self.ins_right_neigh

        # self.del_start_pos
        # self.del_end_pos
        # self.del_start_neighbour
        # self.del_end_neighbour

        ####################################

        ####################################

        # iidx = 0
        # while True:
        #     if self.inserted_object['left_neigh'].iloc[iidx] ==

        # didx = 0
        # for isp, iep, iln, irn in zip(*self.inserted_object.values.transpose()):
        # for dsp, dep, dln, drn in
        # zip(*self.deleted_object.values.transpose()):

        # for isp, iep, iln, irn in
        # zip(*self.inserted_object.values.transpose()):

        #         if iln

        #cols = list(set(self.inserted_object.values.dtype.names).intersection(self.deleted_object.values.dtype.names))
        #result = recfunctions.join_by(cols, self.inserted_object, self.deleted_object, jointype='outer')
        # import ipdb; ipdb.set_trace()  # breakpoint 675a27f4 //

        # if len(self.change) > 0:
        #     import numpy.lib.recfunctions as recfunctions
        #     import ipdb; ipdb.set_trace()  # breakpoint 3a322cf2 //

        #     cols = list(set(self.inserted_object.values.dtype.names).intersection(self.deleted_object.values.dtype.names))
        #     result = recfunctions.join_by(cols, self.inserted_object, self.deleted_object, jointype='outer')
        #     import ipdb; ipdb.set_trace()  # breakpoint 675a27f4 //

        self.change.fillna(-1, inplace=True)
        self.change["left_neigh"] = self.change["left_neigh"].astype(int)
        self.change["right_neigh"] = self.change["right_neigh"].astype(int)
        self.change["ins_start_pos"] = self.change["ins_start_pos"].astype(int)
        self.change["ins_end_pos"] = self.change["ins_end_pos"].astype(int)
        self.change["del_start_pos"] = self.change["del_start_pos"].astype(int)
        self.change["del_end_pos"] = self.change["del_end_pos"].astype(int)

    def append_neighbour_vec(self, to_rev, epsilon_size):
        self.wiki_who_tokens = self.tokens
        self.wiki_who_tokens_str = self.values
        del self.values
        del self.tokens

        neighbour_df = self.change.apply(
            self.find_tokens, axis=1, args=(self, to_rev, epsilon_size))

        if len(neighbour_df) > 0:
            neighbour_df.columns = columns
        else:
            neighbour_df = pd.DataFrame(columns=columns)
        self.change_df = pd.concat(
            [self.change, neighbour_df], sort=False, axis=1)

    def find_tokens(self, change, revision, to_rev, epsilon_size):

        start_left = (change["left_neigh"] - epsilon_size)
        if start_left < 0:
            start_left = 0
        left_neigh = slice(start_left, change["left_neigh"] + 1)

        end_right = (change["right_neigh"] + epsilon_size + 1)
        if end_right >= revision.wiki_who_tokens.size:
            end_right = revision.wiki_who_tokens.size - 1
        right_neigh = slice(change["right_neigh"], end_right)
        if(change["ins_start_pos"] == -1):
            ins_tokens = []
            ins_tokens_str = []
        else:
            ins_slice = slice(change["ins_start_pos"],
                              change["ins_end_pos"] + 1)
            ins_tokens = to_rev.tokens[ins_slice].tolist()
            ins_tokens_str = to_rev.values[ins_slice]

        if(change["del_start_pos"] == -1):
            del_tokens = []
            del_tokens_str = []
        else:
            del_slice = slice(change["del_start_pos"],
                              change["del_end_pos"] + 1)
            del_tokens = revision.wiki_who_tokens[del_slice].tolist()
            del_tokens_str = revision.wiki_who_tokens_str[del_slice]

        left_token = revision.wiki_who_tokens[left_neigh].tolist()
        right_token = revision.wiki_who_tokens[right_neigh].tolist()
        left_token_str = revision.wiki_who_tokens_str[left_neigh]
        right_token_str = revision.wiki_who_tokens_str[right_neigh]
        return pd.Series([
            ins_tokens, del_tokens,
            tuple(ins_tokens_str), tuple(del_tokens_str),
            left_neigh, right_neigh,
            left_token, right_token,
            tuple(left_token_str), tuple(right_token_str)])

    # def find_tokens(self, change, revision, to_rev, epsilon_size):
    #     start_left = (int(change["left_neigh"]) - epsilon_size)
    #     if start_left < 0:
    #         start_left = 0
    #     left_neigh = slice(start_left, int(change["left_neigh"]) + 1)

    #     end_right = (int(change["right_neigh"]) + epsilon_size + 1)
    #     if end_right >= revision.wiki_who_tokens.size:
    #         end_right = revision.wiki_who_tokens.size - 1
    #     right_neigh = slice(int(change["right_neigh"]), end_right)
    #     if(change["ins_start_pos"] == -1):
    #         ins_tokens = []
    #     else:
    #         ins_slice = slice(int(change["ins_start_pos"]), int(
    #             change["ins_end_pos"] + 1))
    #         ins_tokens = to_rev.tokens[ins_slice]
    #     if(change["del_start_pos"] == -1):
    #         del_tokens = []
    #     else:
    #         del_slice = slice(int(change["del_start_pos"]), int(
    #             change["del_end_pos"] + 1))
    #         del_tokens = revision.wiki_who_tokens[del_slice]
    #     left_token = revision.wiki_who_tokens_str[left_neigh]
    #     right_token = revision.wiki_who_tokens_str[right_neigh]
    #     return pd.Series([
    #         tuple(ins_tokens), tuple(del_tokens),
    #         left_neigh, right_neigh,
    #         left_neigh, right_neigh,
    #         tuple(left_token), tuple(right_token)])
