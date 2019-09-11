
from wikiwho_chobj import Chobjer
from wikiwho_chobj.utils import Timer
from wikiwho_chobj_pd import Chobjer as ChobjerPD

import pandas as pd

if __name__ == "__main__":

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

        df_new = pd.DataFrame(chobs1, columns=chobs1[0].keys())

        df_new = df_new.sort_values([
            'page_id', 'from_rev', 'to_rev', 'from_timestamp',
            'to_timestamp', 'editor', 'ins_start_pos', 'ins_end_pos']).reset_index(drop=True)

        copd = ChobjerPD(article=_id, pickles_path='pickles',
                       lang='en', context=5)
        with Timer():
            chobs2 = [x for x in copd.iter_chobjs()]

        df_old = pd.DataFrame(chobs2, columns=chobs2[0].keys())

        df_old = df_old.sort_values([
            'page_id', 'from_rev', 'to_rev', 'from_timestamp',
            'to_timestamp', 'editor', 'ins_start_pos', 'ins_end_pos']).reset_index(drop=True)
        print(len(df_old))

        if not df_old.equals(df_new):
            if df_old.columns.equals(df_new.columns):
                for c in df_old.columns:
                    if not df_old[c].equals(df_new[c]):
                        print('Different values for: ' + c)

            else:
                print('diff cols')
            print(sum(df_old['text'] != df_new['text']))
        else:
            print('equal dataframes')
