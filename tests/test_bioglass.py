from wikiwho_chobj import Chobjer
import pandas as pd


# THIS test is no longer necessary, at least for now
# def test_wikiwho_api():
#     df_api = pd.read_hdf("data/change objects/Bioglass_change.h5")
#     df_aadil = pd.read_hdf("data/change objects/Bioglass_change_aadil.h5")
#     assert df_aadil.equals(df_api)


def test_wikiwho_pickle():
    df_pickle_api = pd.read_hdf("data/change objects/2161298_change.h5")
    df_aadil = pd.read_hdf("data/change objects/Bioglass_change_aadil.h5")
    assert df_aadil.equals(df_pickle_api.drop(
        columns=['ins_tokens_str', 'del_tokens_str', 'left_token_str', 'right_token_str']))

    for col in df_aadil.columns:
        assert df_aadil[col].equals(df_pickle_api[col])

    assert df_aadil.index.equals(df_pickle_api.index)

