import pkg_resources
name = "wikiwho_chobj"
try:
    __version__ = pkg_resources.require(name)[0].version
except:
    __version__ = None


from .chobj import Chobjer
from . import utils



class ChobjerPickle(Chobjer):

    def __init__(self, ww_pickle, context, starting_revid = -1):
        self.ww_pickle = ww_pickle       
        self.article = self.ww_pickle.page_id
        self.context = context
        self.revisions = self.ww_pickle.revisions
        self.starting_revid = starting_revid
