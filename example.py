from chober import Chober 


if __name__ == "__main__":
    # co = Chober(article=2161298, pickles_path='pickles', lang='en', context=5)

    #co.get_dummy_chobs()


    # for i in range(10):
    #     print('\n')
    #     co.get_chobs(i,i+1)



    import os

    #import pandas as pd
    from wikiwho_chobj import Chobjer
    from wikiwho_chobj.utils import Timer

    ids = [2161298, 1620389, 6187]
    #ids = [6886]

    print('x')
    for _id in ids:
        co = Chobjer(article=_id, pickles_path='pickles', lang='en', context=4)

        with Timer():
            chobs1 = [x for x in co.iter_chobjs()]
        print(len(chobs1))



# import os

# import pandas as pd
# from wikiwho_chobj import Chobjer

# if __name__ == "__main__":
#     co = Chobjer(article=2161298, pickles_path='pickles', lang='en', context=5)
#     df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())





