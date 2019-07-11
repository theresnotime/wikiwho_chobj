from biochober import Chober

from pprint import pprint

from chober.timer import Timer



def print_dict(_d, vals = ['ins_tokens_str', 'del_tokens_str', 'left_token_str', 'right_token_str']):
    print( {x:_d[x] for x in vals})


if __name__ == "__main__":
    #co = Chober(article=6187, pickles_path='pickles', lang='en', context=5)
    co = Chober(article=2161298, pickles_path='pickles', lang='en', context=5)
    #co = Chober(article=1620389, pickles_path='pickles', lang='en', context=5)

    co.get_dummy_chobs()


    co.get_chobs(5,6)
