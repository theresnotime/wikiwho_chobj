import traceback


class Wiki:
    '''
    MAIN CLASS TO store all revisions for a wiki along with editors and timestamp.
    '''

    def __init__(self, article, revs, tokens):
        #self.id = id
        self.article = article
        self.revisions = revs
        self.add_all_token(tokens)

    def add_all_token(self, tokens):
        for token in tokens:
            # token.str
            self.revisions[token.origin_rev_id].added.append(token.token_id)
            for in_revision in token.inbound:
                self.revisions[in_revision].added.append(token.token_id)
            for out_revision in token.outbound:
                self.revisions[out_revision].removed.append(token.token_id)
