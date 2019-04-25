from wiki import Wiki
from revision import Revision
from wikiwho_wrapper import WikiWho
import pandas as pd
import cred
from time import sleep
import pickle
import numpy as np
import traceback
import os

class ChangeObject:

	def __init__(self, article_name, epsilon_size):
		self.article_name = article_name
		self.epsilon_size = epsilon_size

	def create_change_object(self, article_name, content_dir = "../data/content/", 
                            change_object_dir =  "../data/change objects/", epsilon_size=30, save=False):
    
	    content_filepath = os.path.join(content_dir, article_name+".h5")
	    change_object_filepath = os.path.join(change_object_dir, article_name+".pkl")
	    
	    with pd.HDFStore(content_filepath, 'r') as store:
	        #retrieving all rev list and change object from file
	        rev_list = store.get("rev_list")
	        all_rev = store.get("all_tokens")
	        all_tokens = all_rev.to_dict(orient="records")
	        
	        #making revision objects
	        revs = rev_list.apply(lambda rev: Revision(rev["id"],rev["timestamp"], rev["editor"]),axis=1)
	        revs.index = rev_list.id
	        
	        # Getting first revision object and adding content ot it
	        from_rev_id = revs.index[0]
	        wiki = Wiki(article_name, revs, all_tokens)

	        wiki.revisions.iloc[0].content = store["r"+str(from_rev_id)] 
	        # adding content to all other revision and finding change object between them.
	        
	        for to_rev_id in list(revs.index[1:]):
	            key="r"+str(to_rev_id)
	            to_rev_content = store[key]
	            wiki.create_change(from_rev_id, to_rev_id, to_rev_content, epsilon_size)
	            from_rev_id = to_rev_id
	         
	    if save:
	        with open(change_object_filepath, "wb") as file:
	            pickle.dump(wiki, file)
	        
	    return wiki

	def was_added(self, x, revision):
	    i = x["in"]
	    o = x["out"]
	    i_cleaned = []
	    o_cleaned = []
	    for rev in i:
	        if rev <= revision:
	            i_cleaned.append(rev)
	    for rev in o:
	        if rev <= revision:
	            o_cleaned.append(rev)
	    if (len(i_cleaned) == len(o_cleaned)):
	        x.added = True
	    return x

	def add_start_end_token(self, df, add_false=True):
	    if add_false:
	        df.loc[len(df)] = ["{$nd}", -2, False]
	        df.loc[-1] = ["{st@rt}", -1, False]
	    else:
	        df.loc[len(df)] = ["{$nd}", -2]
	        df.loc[-1] = ["{st@rt}", -1]      
	    df.index = df.index+1
	    df.sort_index(inplace=True)
	    return df

	def df_rev_content(self, key, first=False):
	    rev_content = self.ww.api.specific_rev_content_by_rev_id(key, o_rev_id=False, editor=False)["revisions"][0][str(key)]["tokens"]
	    rev_content = pd.DataFrame(rev_content)
	    rev_content["added"] = pd.Series(np.full((len(rev_content),), False))
	    rev_content = rev_content.apply(lambda x: self.was_added(x, key),axis=1)
	    del rev_content["in"]
	    del rev_content["out"]
	    rev_content = self.add_start_end_token(rev_content)
	    return rev_content

	def get_str_tokenid_for_rev(self, rev):
	    strs = [tok["str"] for tok in self.ww.dv.api.specific_rev_content_by_rev_id(key)["revisions"][0][str(key)]["tokens"]]
	    tokens = [tok["token_id"] for tok in self.ww.dv.api.specific_rev_content_by_rev_id(key)["revisions"][0][str(key)]["tokens"]]
	    rev_len_list = pd.DataFrame({"str": strs, "token_id": tokens})
	    rev_len_list = self.add_start_end_token(rev_len_list, add_false=False)
	    return rev_len_list

	def create(self):
		self.ww = WikiWho(protocol="http", domain="10.6.13.139")

		r_ids = self.ww.api.rev_ids_of_article("Bioglass")
		rev_list = pd.DataFrame(r_ids["revisions"])
		all_rev = pd.DataFrame(self.ww.api.all_content("Bioglass")["all_tokens"])
		del all_rev["editor"]
		all_tokens = all_rev.to_dict(orient="records")

		#making revision objects
		revs = rev_list.apply(lambda rev: Revision(rev["id"],rev["timestamp"], rev["editor"]),axis=1)
		revs.index = rev_list.id

		# Getting first revision object and adding content ot it
		from_rev_id = revs.index[0]
		self.wiki = Wiki(self.article_name, revs, all_tokens)

		self.wiki.revisions.iloc[0].content = self.df_rev_content(from_rev_id, first=True)
		# adding content to all other revision and finding change object between them.

		for to_rev_id in list(revs.index[1:]):
		    to_rev_content = self.df_rev_content(to_rev_id)
		    self.wiki.create_change(from_rev_id, to_rev_id, to_rev_content, self.epsilon_size)
		    from_rev_id = to_rev_id
		    #sleep(1)

	def save(self, save_dir):
		save_filepath = os.path.join(save_dir, self.article_name+"_change.pkl")
		with open(save_filepath, "wb") as file:
			pickle.dump(self.wiki, file)


if __name__ == "__main__":
	epsilon_size=30
	article_name = 'Bioglass'
	change_object_dir = "data/change objects/"
	co = ChangeObject(article_name, epsilon_size)
	co.create()
	co.save(change_object_dir)