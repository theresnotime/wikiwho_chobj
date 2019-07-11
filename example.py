from chober import Chober

from pprint import pprint

from chober.timer import Timer



def print_dict(_d, vals = ['ins_tokens_str', 'del_tokens_str', 'left_token_str', 'right_token_str']):
    print( {x:_d[x] for x in vals})


if __name__ == "__main__":
    #co = Chober(article=6187, pickles_path='pickles', lang='en', context=5)
    # co = Chober(article=2161298, pickles_path='pickles', lang='en', context=5)
    #co = Chober(article=1620389, pickles_path='pickles', lang='en', context=5)
    

    # for x in co._get_chobs_iter(207780901, 207995408):
    #     pprint(x)

    

    # for x in co.get_chobs_iter(5,6):
    #     pprint(x)

    # co.get_all_chobs()

    # with Timer(silent=False):
    #     chobs1 = [x for x in co.get_all_chobs_iter()]
    # print(len(chobs1))

    # for x in range(1000,1100):
    #     co.get_chobs_iter(x,x+1)

    #print(f'zip: {co.zip}')
    #print(f'nonzip: {co.nonzip}')

    # co.get_dummy_chobs()

    # co.get_chobs(5,6)

    # for i in range(10):
    #     print('\n' + str(i))
    #     co.get_chobs(i,i+1)

    import os

    #import pandas as pd
    from wikiwho_chobj import Chobjer

    #co = Chobjer(article=6187, pickles_path='pickles', lang='en', context=4)
    co = Chobjer(article=2161298, pickles_path='pickles', lang='en', context=4)
    #co = Chobjer(article=1620389, pickles_path='pickles', lang='en', context=4)

    with Timer(silent=False):
        chobs2 = [x for x in co.iter_chobjs()]
    print(len(chobs2))

    notfound1 = []
    for (i,x) in enumerate(chobs1):
        found = False
        for y in chobs2:
            if (x['from_rev'] == y['from_rev'] and 
                set(x['ins_tokens']) == set(y['ins_tokens']) and 
                set(x['del_tokens']) == set(y['del_tokens'])):
                found = True
                break
        if not found:
            notfound1.append((i, x['from_rev'], x['to_rev']))


    print('--')
    print('--')        
    print(f'Not found: {len(notfound1)}')
    # idx = 0
    # print(notfound1[idx][1])
    # print(notfound1[idx][2])
    
    # #print(f'Not found: {notfound1}')

    # for (i,x) in enumerate(chobs1):
    #     if x['from_rev'] == notfound1[idx][1]:
    #         print_dict(x)

    # print('--')

    # for (i,x) in enumerate(chobs2):
    #     if x['from_rev'] == notfound1[idx][1]:
    #         print_dict(x)



    notfound2 = []
    for (i,x) in enumerate(chobs2):
        found = False
        for y in chobs1:
            if (x['from_rev'] == y['from_rev'] and 
                set(x['ins_tokens']) == set(y['ins_tokens']) and 
                set(x['del_tokens']) == set(y['del_tokens'])):
                found = True
                break
        if not found:
            notfound2.append((i, x['from_rev'], x['to_rev']))

    print('--')
    print('--')
    print(f'Not found: {len(notfound2)}')

    # idx = 0
    # print(notfound2[idx][1])
    # print(notfound2[idx][2])
    # #print(f'Not found: {notfound2}')

    # for (i,x) in enumerate(chobs1):
    #     if x['from_rev'] == notfound2[idx][1]:
    #         print_dict(x)

    # print('--')

    # for (i,x) in enumerate(chobs2):
    #     if x['from_rev'] == notfound2[idx][1]:
    #         print_dict(x)


