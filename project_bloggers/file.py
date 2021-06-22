import requests
from tqdm.auto import tqdm
import pandas as pd
from tqdm import tqdm
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from pymystem3 import Mystem
import collections
import sqlite3 as sql
import datetime

def get_posts(id_group):
    token = 'dcd83c13dcd83c13dcd83c1370dca00d5eddcd8dcd83c13bc1a020f12ad7f13075ea9b7'
    version = '5.92'
    wall_get_url = "https://api.vk.com/method/wall.get"
    c = [100, 200, 300]
    group_posts = []
    for p in c:
        data = requests.get(
            wall_get_url,
            params={
                "owner_id": -id_group,  # ID юзера
                "count": p,  # кол-во постов
                "v": version, # версия API
                "access_token": token  # токен доступа
            }
            ).json()
        if 'error' not in data:
            for item in data['response']['items']:
                posts_info = {}
                posts_info['text'] = item['text']
                if posts_info['text']:
                    group_posts.append(posts_info)
    return(group_posts)

def make_df(group_posts):
    df = pd.DataFrame(group_posts)
    return(df)

def lemmatize(text):
    m = Mystem()
    text = ''.join(m.lemmatize(text))
    text = re.sub(r'\n+', ' ', text)
    return text

def remove_stop_words(text):
    stop_words = stopwords.words('russian')
    stop_words.extend([
                        'что', 'это', 'так', 'вот', 'быть', 'как', 'на', 
                        'который', 'мочь', 'наш', 'ваш', 'их', 'свой', 'иной', 'то', ',',
                        ])
    return ' '.join([word for word in text.split() if not word in stop_words])

def most_popular_words(df, c):
    tokens = []
    for lines in df['text_lemm']:
        a = lines.split()
        tokens.append(a)
    for l in tokens:
        for w in l:
            c[w] += 1
    most_popular = c.most_common(20)
    return(most_popular)

with sql.connect("my_db") as con:
    con.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol_count INTEGER, symbol VARCHAR(255), post_time TIMESTAMP, group_id INTEGER);")
    cursor = con.cursor()
    cursor.execute("DELETE FROM posts WHERE 1=1")

all_c = collections.Counter()
print("Parsing")
id_groups = [
                121304138, 41768412, 43074088, 73247559, 83853569, 40034115, 
                185073409, 88799721, 104433541, 66687279, 84930809, 97385648, 
                104168133, 167923566, 81820554, 101209760, 46576367
            ]
posts = []
d = datetime.datetime.now()
for i, group_id in enumerate(id_groups):
    c = collections.Counter()
    print("Data is got for {}".format(group_id))
    posts = get_posts(group_id)

    print("Lemmatization")
    df = make_df(posts)
    df["text_lemm"] = df["text"].apply(lambda x: lemmatize(x))

    print("Clearing")
    df["text_lemm"] = df["text_lemm"].apply(lambda x: remove_stop_words(x))

    print("most popular")
    tokens = []
    for lines in df['text_lemm']:
        a = lines.split()
        tokens.append(a)
    for l in tokens:
        for w in l:
            c[w] += 1
            all_c[w] += 1
    most_popular = c.most_common(20)
    with sql.connect('my_db') as con:
        cursor = con.cursor()
        for count, name in most_popular:
            cursor.execute("INSERT INTO posts (symbol, symbol_count, post_time, group_id) VALUES (?, ?, ?, ?)", (name, count, d, group_id))

with sql.connect('my_db') as con:
    cursor = con.cursor()
    most_popular = all_c.most_common(20)
    for count, name in most_popular:
        cursor.execute("INSERT INTO posts (symbol, symbol_count, post_time, group_id) VALUES (?, ?, ?, ?)", (name, count, d, 0))