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
            self.revisions.loc[token.origin_rev_id].added.add(token.token_id)
            for in_revision in token.inbound:
                self.revisions.loc[in_revision].added.add(token.token_id)
            for out_revision in token.outbound:
                self.revisions.loc[out_revision].removed.add(token.token_id)

    def create_change(self, from_rev_id, to_rev_id, to_rev_content, epsilon_size):
        try:
            from_rev = self.revisions[from_rev_id]
            to_rev = self.revisions[to_rev_id]
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
