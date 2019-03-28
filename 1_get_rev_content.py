import requests
import numpy as np
import pandas as pd
import os
import traceback

from wikiwho import open_pickle
from WikiWho.wikiwho import Wikiwho as BaseWikiwho
import pdb

def get_contents(baseurl, content, start_rev_id, end_rev_id, ww_object):
    pdb.set_trace()

    content_url = os.path.join(baseurl, "rev_content", content, str(start_rev_id)+"/")
    if end_rev_id:
        content_url = os.path.join(content_url, str(end_rev_id)+"/")
    params = { "o_rev_id": "false", "editor": "false", "token_id": "true", "in": "false", "out": "false" }
    try:
        response = requests.get(content_url, params= params)
        if response.status_code == requests.codes.ok: 
            response = response.json()
            if "revisions" in response.keys() :
                return response["revisions"]
            elif "revisions" not in response.keys() : 
                raise AttributeError("Server did not return revisions key it returned \t"+response.keys())
        elif response.status_code != requests.codes.ok : 
            print(content_url)
            raise AttributeError("Server returned bad code\t"+response.status_code)
    except:
        print(traceback.format_exc())

#pads each revisions content with a start and end 
def tokens_to_df(tokens):
    tokens.insert(0, {'token_id':-1, 'str':  "{st@rt}"})
    tokens.append({'token_id':-2, 'str': "{$nd}"})
    return pd.DataFrame(tokens)

def save_content(revison_series, filename, content, ww_object, step=200, baseurl="https://api.wikiwho.net/en/api/v1.0.0-beta/"):
    end_index = revison_series.size
    from_index = 0
    with pd.HDFStore(filename, 'a') as store:
        try:
            for to_index in  range(0, end_index, step):    
                rev_contents = get_contents(baseurl, content, str(revison_series[from_index]), str(revison_series[to_index]), ww_object=ww_object)
                from_index = to_index
                for rev_content in rev_contents:
                    key = "r"+list(rev_content.keys())[0]
                    df = tokens_to_df(list(rev_content.values())[0]["tokens"])
                    store.put(key, df, table=False)
            to_index = from_index + (end_index-1)%step
            rev_contents = get_contents(baseurl, content, str(revison_series[from_index]), str(revison_series[to_index]), ww_object=ww_object)
            rev_contents.extend(get_contents(baseurl, content, str(revison_series[to_index])))
            for rev_content in rev_contents:
                key = "r"+list(rev_content.keys())[0]
                df = tokens_to_df(list(rev_content.values())[0]["tokens"])
                store.put(key, df, table=False)
        except:
            print("problem ", traceback.format_exc())


def save_article(article_name, ww_object, baseurl="https://api.wikiwho.net/en/api/v1.0.0-beta/", save_dir = "data/content", step=200):
    filename = article_name + ".h5"

    rev_list_df = pd.DataFrame(columns=["editor", "id", "timestamp"])
    i = 0
    for rev_id in ww_object.ordered_revisions:
        rev = {'id': rev_id}
        revision = ww_object.revisions[rev_id]
        rev['editor'] = revision.editor
        rev['timestamp'] = revision.timestamp
        rev_list_df.loc[i] = rev
        i += 1 

    save_path = os.path.join(save_dir, filename)
    
    all_tokens_df = pd.DataFrame(columns=['in', 'o_rev_id', 'out', 'str', 'token_id'])
    i = 0
    for word in ww_object.tokens:
        token = dict()
        token['str'] = word.value
        token['o_rev_id'] = word.origin_rev_id
        token['token_id'] = word.token_id
        token['in'] = word.inbound
        token['out'] = word.outbound
        all_tokens_df.loc[i] = token

    with pd.HDFStore(save_path, 'a') as store:
        store.put("rev_list", rev_list_df, table=False)
        store.put("all_tokens", all_tokens_df, table=False)

    save_content(rev_list_df["id"], save_path, article_name, ww_object=ww_object, step=step)




# In[8]:

if __name__ == "__main__":
    obj = open_pickle(6187, lang='en')

    #  local query
    all_content = obj.get_all_content(['o_rev_id', 'editor', 'token_id', 'in', 'out', 0])
    
    save_article(article_name="Cologne", ww_object=obj)

    #article_series=pd.read_csv("conflicted_article.csv")["articles"]
    # article_series = ["Berlin Wall", "Bioglass", "Hummus", "Andy Murray", "Istanbul"]
    # print("starting download for the conflicted articles")
    # for article in article_series:
    #     print("Processing the article", article)    
    #     save_article(article)
    # print("finishing download")

