import os

import pandas as pd

from wikiwho_chobj import Chobjer

from wikiwho_wrapper import WikiWho

if __name__ == "__main__":
    epsilon_size = 30
    change_object_dir = "data/change objects/"

    # REMOTE
    #ww = WikiWho(protocol="http", domain="10.6.13.139")
    #co = Chobjer(ww, "Bioglass", epsilon_size)

    # LOCAL
    ww = WikiWho(pickle_path='pickles', lng='en')
    co = Chobjer(ww, 2161298, epsilon_size)

    data = [chobj for chobj in co.iter_chobjs()]
    df = pd.DataFrame(data, columns = data[0].keys())

    change_dataframe_path = os.path.join(
            change_object_dir, f"{co.article_name}_change_iter.h5")
    df.to_hdf(change_dataframe_path, key="data", mode='w')


    co.create()
    co.save(change_object_dir)
    co.save_hd5(change_object_dir)

