
from wikiwho_chobj import Chobjer, ChobjerPickle
from wikiwho_chobj.utils import Timer
from wikiwho import open_pickle


if __name__ == "__main__":

    starting_revid = -1
    #ids = [2161298, 1620389, 6187]
    ids = [2161298]
    #ids = [6886]
    #ids = [2161298]
    
    # to test with id
    #ids = [2161298]
    #starting_revid = 855387192

    for _id in ids:

        ww_pickle = open_pickle(_id, pickle_path='pickles', lang='en')
        co = ChobjerPickle(ww_pickle=ww_pickle, context=5, starting_revid=starting_revid)
        with Timer():
            chobs2 = [x for x in co.iter_chobjs()]

        co = Chobjer(article=_id, pickles_path='pickles', lang='en', 
            context=5, starting_revid=starting_revid)
        with Timer():
            chobs1 = [x for x in co.iter_chobjs()]



