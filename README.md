# wikiwho_chobj

Creates change objects based on WikiWho. A change object represent a contigous edition in Wikipedia that occurred between two consecutive revision. It contains the inserted and deleted tokens, as well as the left and right context in which the changes ocurred. 

It also contains the revisions, timestamps and editor of the change, as well as the positions of the change in the respective revision

# How to use it?


1. Create a Chobjer object using the id of the Wikipedia article. The *Bioglass* article (`id = 2161298`) is provided in the Github repository as an example. If you need other articles please [contact us](https://api.wikiwho.net/contact/).

```
from wikiwho_chobj import Chobjer

chobjer = Chobjer(2161298, 'pickles', 'en', 30)
```

2. You can iterate over the change objects using the `iter_objets()` method:

```
for chobjer.iter_chobjs()
	chobjer.iter_chobjs()
```

3. Or create a dataframe with it

```
import pandas as pd

df = pd.DataFrame(co.iter_chobjs(), columns = next(co.iter_chobjs()).keys())
```