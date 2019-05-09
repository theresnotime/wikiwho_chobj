import os

import pandas as pd
from wikiwho_chobj import Chobjer

if __name__ == "__main__":
    co = Chobjer(article=2161298, pickles_path='pickles', lang='en', context=5)
    df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())

