import requests
from tqdm.auto import tqdm
import pandas as pd
from tqdm import tqdm
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from pymystem3 import Mystem
import collections

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

def prepare_data(id_posts):
	c = collections.Counter()
	print("parsing")
	posts = []
	for post_id in id_posts:
		posts += get_posts(post_id)

	df = pd.DataFrame(posts)
	print("lemmotization")
	df['text_lemm'] = df['text'].apply(lambda x: lemmatize(x))
	print("removing stop words")
	df['text_lemm'] = df['text_lemm'].apply(lambda x: remove_stop_words(x))
	print("getting popular words")
	most_popular = most_popular_words(df, c)
	return most_popular