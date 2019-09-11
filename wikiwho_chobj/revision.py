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

    def iter_chobs(self, page_id, to_rev, epsilon_size):
        removed = np.isin(self.tokens,
                          to_rev.removed, assume_unique=True).astype(np.int)
        ediff = np.ediff1d(
            np.pad(removed, (1, 1), mode="constant", constant_values=0))
        del_start_pos = np.nonzero(ediff == 1)[0]
        del_end_pos = np.nonzero(ediff == -1)[0] - 1
        del_left_neigh = del_start_pos - 1
        del_right_neigh = del_end_pos + 1

        ins_left_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.start_token_id, assume_unique=True))[0]
        ins_right_neigh = np.nonzero(
            np.isin(self.tokens, to_rev.end_token_id, assume_unique=True))[0]

        did = 0
        iid = 0

        chdata = []

        while iid < len(ins_left_neigh) and did < len(del_left_neigh):

            if (ins_left_neigh[iid] == del_left_neigh[did] and
                    ins_right_neigh[iid] == del_right_neigh[did]):

                isp = to_rev.ins_start_pos[iid]
                iep = to_rev.ins_end_pos[iid]
                ln = ins_left_neigh[iid]
                rn = ins_right_neigh[iid]
                dsp = del_start_pos[did]
                dep = del_end_pos[did]

                ins_slice = slice(isp, iep + 1)
                del_slice = slice(dsp, dep + 1)

                ln_slice = slice(max(0, ln - epsilon_size), ln + 1)
                rn_slice = slice(
                    rn, min(rn + epsilon_size + 1, self.tokens.size - 1))

                yield {
                    'page_id': page_id,
                    'from_rev': self.id,
                    'to_rev': to_rev.id,
                    'from_timestamp': to_rev.timestamp,
                    'to_timestamp': self.timestamp,
                    'editor': to_rev.editor,
                    'ins_start_pos': int(isp),
                    'ins_end_pos': int(iep),
                    'left_neigh': int(ln),
                    'right_neigh': int(rn),
                    'del_start_pos': int(dsp),
                    'del_end_pos': int(dep),
                    'ins_tokens_str': tuple(to_rev.values[ins_slice]),
                    'del_tokens_str': tuple(self.values[del_slice]),
                    'left_token_str': tuple(self.values[ln_slice]),
                    'right_token_str': tuple(self.values[rn_slice]),
                    'ins_tokens': to_rev.tokens[ins_slice].tolist(),
                    'del_tokens': self.tokens[del_slice].tolist(),
                    'left_token': self.tokens[ln_slice].tolist(),
                    'right_token': self.tokens[rn_slice].tolist(),
                    'text': (tuple(self.values[ln_slice]),
                             tuple(to_rev.values[ins_slice]),
                             tuple(self.values[del_slice]),
                             tuple(self.values[rn_slice])),
                }

                did += 1
                iid += 1
            elif (ins_left_neigh[iid] <= del_left_neigh[did]):

                isp = to_rev.ins_start_pos[iid]
                iep = to_rev.ins_end_pos[iid]
                ln = ins_left_neigh[iid]
                rn = ins_right_neigh[iid]
                dsp = -1
                dep = -1

                ins_slice = slice(isp, iep + 1)

                ln_slice = slice(max(0, ln - epsilon_size), ln + 1)
                rn_slice = slice(
                    rn, min(rn + epsilon_size + 1, self.tokens.size - 1))

                yield {
                    'page_id': page_id,
                    'from_rev': self.id,
                    'to_rev': to_rev.id,
                    'from_timestamp': to_rev.timestamp,
                    'to_timestamp': self.timestamp,
                    'editor': to_rev.editor,
                    'ins_start_pos': int(isp),
                    'ins_end_pos': int(iep),
                    'left_neigh': int(ln),
                    'right_neigh': int(rn),
                    'del_start_pos': int(dsp),
                    'del_end_pos': int(dep),
                    'ins_tokens_str': tuple(to_rev.values[ins_slice]),
                    'del_tokens_str': tuple(),
                    'left_token_str': tuple(self.values[ln_slice]),
                    'right_token_str': tuple(self.values[rn_slice]),
                    'ins_tokens': to_rev.tokens[ins_slice].tolist(),
                    'del_tokens': [],
                    'left_token': self.tokens[ln_slice].tolist(),
                    'right_token': self.tokens[rn_slice].tolist(),
                    'text': (tuple(self.values[ln_slice]),
                             tuple(to_rev.values[ins_slice]),
                             tuple(),
                             tuple(self.values[rn_slice])),
                }

                iid += 1
            elif (ins_left_neigh[iid] > del_left_neigh[did]):
                isp = -1
                iep = -1
                ln = del_left_neigh[did]
                rn = del_right_neigh[did]
                dsp = del_start_pos[did]
                dep = del_end_pos[did]

                del_slice = slice(dsp, dep + 1)

                ln_slice = slice(max(0, ln - epsilon_size), ln + 1)
                rn_slice = slice(
                    rn, min(rn + epsilon_size + 1, self.tokens.size - 1))

                yield {
                    'page_id': page_id,
                    'from_rev': self.id,
                    'to_rev': to_rev.id,
                    'from_timestamp': to_rev.timestamp,
                    'to_timestamp': self.timestamp,
                    'editor': to_rev.editor,
                    'ins_start_pos': int(isp),
                    'ins_end_pos': int(iep),
                    'left_neigh': int(ln),
                    'right_neigh': int(rn),
                    'del_start_pos': int(dsp),
                    'del_end_pos': int(dep),
                    'ins_tokens_str': tuple(),
                    'del_tokens_str': tuple(self.values[del_slice]),
                    'left_token_str': tuple(self.values[ln_slice]),
                    'right_token_str': tuple(self.values[rn_slice]),
                    'ins_tokens': [],
                    'del_tokens': self.tokens[del_slice].tolist(),
                    'left_token': self.tokens[ln_slice].tolist(),
                    'right_token': self.tokens[rn_slice].tolist(),
                    'text': (tuple(self.values[ln_slice]),
                             tuple(),
                             tuple(self.values[del_slice]),
                             tuple(self.values[rn_slice])),
                }

                did += 1

        # if there is left over inserted tokens
        while iid < len(ins_left_neigh):

            isp = to_rev.ins_start_pos[iid]
            iep = to_rev.ins_end_pos[iid]
            ln = ins_left_neigh[iid]
            rn = ins_right_neigh[iid]
            dsp = -1
            dep = -1

            ins_slice = slice(isp, iep + 1)

            ln_slice = slice(max(0, ln - epsilon_size), ln + 1)
            rn_slice = slice(
                rn, min(rn + epsilon_size + 1, self.tokens.size - 1))

            yield {
                'page_id': page_id,
                'from_rev': self.id,
                'to_rev': to_rev.id,
                'from_timestamp': to_rev.timestamp,
                'to_timestamp': self.timestamp,
                'editor': to_rev.editor,
                'ins_start_pos': int(isp),
                'ins_end_pos': int(iep),
                'left_neigh': int(ln),
                'right_neigh': int(rn),
                'del_start_pos': int(dsp),
                'del_end_pos': int(dep),
                'ins_tokens_str': tuple(to_rev.values[ins_slice]),
                'del_tokens_str': tuple(),
                'left_token_str': tuple(self.values[ln_slice]),
                'right_token_str': tuple(self.values[rn_slice]),
                'ins_tokens': to_rev.tokens[ins_slice].tolist(),
                'del_tokens': [],
                'left_token': self.tokens[ln_slice].tolist(),
                'right_token': self.tokens[rn_slice].tolist(),
                'text': (tuple(self.values[ln_slice]),
                         tuple(to_rev.values[ins_slice]),
                         tuple(),
                         tuple(self.values[rn_slice])),
            }

            iid += 1

        # if there is left over deleted tokens
        while did < len(del_left_neigh):
            isp = -1
            iep = -1
            ln = del_left_neigh[did]
            rn = del_right_neigh[did]
            dsp = del_start_pos[did]
            dep = del_end_pos[did]

            del_slice = slice(dsp, dep + 1)

            ln_slice = slice(max(0, ln - epsilon_size), ln + 1)
            rn_slice = slice(
                rn, min(rn + epsilon_size + 1, self.tokens.size - 1))

            yield {
                'page_id': page_id,
                'from_rev': self.id,
                'to_rev': to_rev.id,
                'from_timestamp': to_rev.timestamp,
                'to_timestamp': self.timestamp,
                'editor': to_rev.editor,
                'ins_start_pos': int(isp),
                'ins_end_pos': int(iep),
                'left_neigh': int(ln),
                'right_neigh': int(rn),
                'del_start_pos': int(dsp),
                'del_end_pos': int(dep),
                'ins_tokens_str': tuple(),
                'del_tokens_str': tuple(self.values[del_slice]),
                'left_token_str': tuple(self.values[ln_slice]),
                'right_token_str': tuple(self.values[rn_slice]),
                'ins_tokens': [],
                'del_tokens': self.tokens[del_slice].tolist(),
                'left_token': self.tokens[ln_slice].tolist(),
                'right_token': self.tokens[rn_slice].tolist(),
                'text': (tuple(self.values[ln_slice]),
                         tuple(),
                         tuple(self.values[del_slice]),
                         tuple(self.values[rn_slice])),
            }

            did += 1
