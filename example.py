import os

import pandas as pd

from wikiwho_chobj import Chobjer
from wikiwho_chobj.utils import Timer


if __name__ == "__main__":
    epsilon_size = 30
    change_object_dir = "data/change objects/"

    # REMOTE
    #ww = WikiWho(protocol="http", domain="10.6.13.139")
    #co = Chobjer(ww, "Bioglass", epsilon_size)

    # LOCAL
    with Timer():
        co = Chobjer(2161298, 'pickles', 'en', epsilon_size)

    with Timer():
        df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())

    change_dataframe_path = os.path.join(
            change_object_dir, f"{co.article}_change_iter.h5")

    df.to_hdf(change_dataframe_path, key="data", mode='w')


    # SAVE the change objects data frames
    #co.create()
    #co.save(change_object_dir)
    #co.save_hd5(change_object_dir)

