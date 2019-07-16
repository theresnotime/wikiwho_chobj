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

    def inserted_continuous_pos(self):
        added = np.isin(self.tokens, self.added,
                        assume_unique=True).astype(np.int)
        ediff = np.ediff1d(
            np.pad(added, (1, 1), mode="constant", constant_values=0))
        self.ins_start_pos = np.nonzero(ediff == 1)[0]
        self.ins_end_pos = np.nonzero(ediff == -1)[0] - 1
        self.start_token_id = self.tokens[self.ins_start_pos - 1]
        self.end_token_id = self.tokens[self.ins_end_pos + 1]

    def create_change_object(self, to_rev, epsilon_size):
        removed = np.isin(self.tokens,
                          to_rev.removed, assume_unique=True).astype(np.int)
        ediff = np.ediff1d(
            np.pad(removed, (1, 1), mode="constant", constant_values=0))
        del_start_pos = np.nonzero(ediff == 1)[0]
        del_end_pos = np.nonzero(ediff == -1)[0] - 1
        del_left_neigh = del_start_pos - 1
        del_right_neigh = del_end_pos + 1

        self.ins_left_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.start_token_id, assume_unique=True))[0]
        self.ins_right_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.end_token_id, assume_unique=True))[0]

        did = 0
        iid = 0

        chdata = []

        while iid < len(self.ins_left_neigh) and did < len(del_left_neigh):

            if (self.ins_left_neigh[iid] == del_left_neigh[did] and
                    self.ins_right_neigh[iid] == del_right_neigh[did]):
                chdata.append((
                    to_rev.ins_start_pos[iid],
                    to_rev.ins_end_pos[iid],
                    self.ins_left_neigh[iid],
                    self.ins_right_neigh[iid],
                    del_start_pos[did],
                    del_end_pos[did]
                ))
                did += 1
                iid += 1
            elif (self.ins_left_neigh[iid] <= del_left_neigh[did]):

                chdata.append((
                    to_rev.ins_start_pos[iid],
                    to_rev.ins_end_pos[iid],
                    self.ins_left_neigh[iid],
                    self.ins_right_neigh[iid],
                    -1,
                    -1
                ))
                iid += 1
            elif (self.ins_left_neigh[iid] > del_left_neigh[did]):
                chdata.append((
                    -1,
                    -1,
                    del_left_neigh[did],
                    del_right_neigh[did],
                    del_start_pos[did],
                    del_end_pos[did]
                ))
                did += 1

        while iid < len(self.ins_left_neigh):
            chdata.append((
                to_rev.ins_start_pos[iid],
                to_rev.ins_end_pos[iid],
                self.ins_left_neigh[iid],
                self.ins_right_neigh[iid],
                -1,
                -1
            ))
            iid += 1

        while did < len(del_left_neigh):
            chdata.append((
                -1,
                -1,
                del_left_neigh[did],
                del_right_neigh[did],
                del_start_pos[did],
                del_end_pos[did]
            ))
            did += 1

        change = pd.DataFrame(chdata, columns=[
            'ins_start_pos', 'ins_end_pos', 'left_neigh', 'right_neigh', 'del_start_pos', 'del_end_pos']).sort_values(
            ['left_neigh', 'right_neigh']).reset_index(drop=True)


        neighbour_df = change.apply(
            self.find_tokens, axis=1, args=(self, to_rev, epsilon_size))

        if len(neighbour_df) > 0:
            neighbour_df.columns = columns
        else:
            neighbour_df = pd.DataFrame(columns=columns)
        self.change_df = pd.concat(
            [change, neighbour_df], sort=False, axis=1)

    def find_tokens(self, change, revision, to_rev, epsilon_size):

        start_left = (change["left_neigh"] - epsilon_size)
        if start_left < 0:
            start_left = 0
        left_neigh = slice(start_left, change["left_neigh"] + 1)

        end_right = (change["right_neigh"] + epsilon_size + 1)
        if end_right >= revision.tokens.size:
            end_right = revision.tokens.size - 1
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
            del_tokens = revision.tokens[del_slice].tolist()
            del_tokens_str = revision.values[del_slice]

        left_token = revision.tokens[left_neigh].tolist()
        right_token = revision.tokens[right_neigh].tolist()
        left_token_str = revision.values[left_neigh]
        right_token_str = revision.values[right_neigh]
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
    #     if end_right >= revision.tokens.size:
    #         end_right = revision.tokens.size - 1
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
    #         del_tokens = revision.tokens[del_slice]
    #     left_token = revision.values[left_neigh]
    #     right_token = revision.values[right_neigh]
    #     return pd.Series([
    #         tuple(ins_tokens), tuple(del_tokens),
    #         left_neigh, right_neigh,
    #         left_neigh, right_neigh,
    #         tuple(left_token), tuple(right_token)])
