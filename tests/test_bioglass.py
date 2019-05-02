from wikiwho_chobj import Chobjer
import pandas as pd


def test_wikiwho_api():
    df_api = pd.read_hdf("data/change objects/Bioglass_change.h5")
    df_aadil = pd.read_hdf("data/change objects/Bioglass_change_aadil.h5")
    assert df_aadil.equals(df_api)


def test_wikiwho_pickle():
    df_pickle_api = pd.read_hdf("data/change objects/2161298_change.h5")
    df_aadil = pd.read_hdf("data/change objects/Bioglass_change_aadil.h5")
    assert df_aadil.equals(df_pickle_api)
