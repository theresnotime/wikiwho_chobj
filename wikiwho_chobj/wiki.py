import traceback


class Wiki:
    '''
    MAIN CLASS TO store all revisions for a wiki along with editors and timestamp.
    '''

    def __init__(self, title, revs, tokens):
        #self.id = id
        self.title = title
        self.revisions = revs
        self.add_all_token(tokens)

    def add_all_token(self, tokens):
        for token in tokens:
            # token.str
            self.revisions[token.origin_rev_id].added.add(token.token_id)
            for in_revision in token.inbound:
                self.revisions[in_revision].added.add(token.token_id)
            for out_revision in token.outbound:
                self.revisions[out_revision].removed.add(token.token_id)

    def create_change(self, from_rev_id, to_rev_id, to_rev_content, epsilon_size):
        try:
            from_rev = self.revisions[from_rev_id]
            to_rev = self.revisions[to_rev_id]

            to_rev.from_id = from_rev.id
            from_rev.to_id = to_rev.id

            from_rev.deleted(to_rev)
            to_rev.content = to_rev_content
            to_rev.inserted_continuous_pos()
            to_rev.inserted_neighbours()
            from_rev.create_change_object(to_rev)
            from_rev.append_neighbour_vec(to_rev, epsilon_size)
        except:
            print("exception occurred in calculating change object",
                  traceback.format_exc())
            print("problem in ", to_rev_content.keys())

    def get_chobjs(self, from_rev_id, to_rev_id, to_rev_content, epsilon_size):
        try:
            from_rev = self.revisions[from_rev_id]
            to_rev = self.revisions[to_rev_id]

            to_rev.from_id = from_rev.id
            from_rev.to_id = to_rev.id

            from_rev.deleted(to_rev)
            to_rev.content = to_rev_content
            to_rev.inserted_continuous_pos()
            to_rev.inserted_neighbours()
            from_rev.create_change_object(to_rev)
            from_rev.append_neighbour_vec(to_rev, epsilon_size)
        except:
            print("exception occurred in calculating change object",
                  traceback.format_exc())
            print("problem in ", to_rev_content.keys())

        for _, chobj in from_rev.change_df.iterrows():

            yield {
                'from_rev': from_rev.id,
                'to_rev': to_rev.id,
                'timegap': to_rev.timestamp - from_rev.timestamp,
                'editor': to_rev.editor,
                'ins_start_pos': chobj['ins_start_pos'],
                'ins_end_pos': chobj['ins_end_pos'],
                'left_neigh': chobj['left_neigh'],
                'right_neigh': chobj['right_neigh'],
                'del_start_pos': chobj['del_start_pos'],
                'del_end_pos': chobj['del_end_pos'],
                'ins_tokens_str': chobj['ins_tokens_str'],
                'del_tokens_str': chobj['del_tokens_str'],
                'left_token_str': chobj['left_token_str'],
                'right_token_str': chobj['right_token_str'],
            }
