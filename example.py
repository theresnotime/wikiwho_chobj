


if __name__ == "__main__":
    # from chober import Chober 
    # co = Chober(article=2161298, pickles_path='pickles', lang='en', context=5)

    # co.get_dummy_chobs()


    # for i in range(10):
    #     print('\n')
    #     co.get_chobs(i,i+1)



    import os
    from wikiwho_chobj import Chobjer
    from wikiwho_chobj.utils import Timer


    from wikiwho_chobj_pd import Chobjer as ChobjerPD

    ids = [2161298, 1620389, 6187]
    #ids = [2161298]
    #ids = [6886]

    print('x')
    for _id in ids:
        print(_id)

        co = Chobjer(article=_id, pickles_path='pickles', lang='en', context=5)

        with Timer():
            chobs1 = [x for x in co.iter_chobjs()]
        print(len(chobs1))
        import pandas as pd
        df1 = pd.DataFrame(chobs1, columns = chobs1[0].keys())

        df1 = df1.sort_values(['page_id', 'from_rev', 'to_rev', 'from_timestamp', 
            'to_timestamp', 'editor', 'ins_start_pos', 'ins_end_pos']).reset_index(drop=True)
       
        co = ChobjerPD(article=_id, pickles_path='pickles', lang='en', context=5)
        with Timer():
            df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())

        df = df.sort_values(['page_id', 'from_rev', 'to_rev', 'from_timestamp', 
            'to_timestamp', 'editor', 'ins_start_pos', 'ins_end_pos']).reset_index(drop=True)
        print(len(df))

        if not df.equals(df1):
            if df.columns.equals(df1.columns):
                for c in df.columns:
                    if not df[c].equals(df1[c]):
                        print('Different values for: ' + c)

            else:
                print('diff cols')
            print(sum(df['text'] != df1['text']))
        else:
            print('equal dataframes')

            # if df.index.equals(df1.index):
            #     for i in df.index:
            #         if not df.iloc[i].equals(df1.iloc[i]):
            #             print('Different values for: ' + str(i))
            # else:
            #     print('diff inddex')

        # for i in df.index:
        #     for c in range(len(df.columns)):
        #         try:
        #             for x in df.iloc[i, c], 
        #         if df.iloc[i, c], 
        








# import os

# import pandas as pd
# from wikiwho_chobj import Chobjer

# if __name__ == "__main__":
#     co = Chobjer(article=2161298, pickles_path='pickles', lang='en', context=5)
#     df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())





