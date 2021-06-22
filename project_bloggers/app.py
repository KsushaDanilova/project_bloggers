from flask import Flask, render_template, jsonify, request
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from parser import prepare_data, get_posts, make_df, lemmatize, remove_stop_words, most_popular_words
from flask_socketio import SocketIO, emit
import pandas as pd
import sqlite3 as sql
import collections
import datetime


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['SECRET_KEY'] = 'secret key'

# manager = Manager(app)

@app.route('/')
def index():
    return render_template('main.html')

# @socketio.on('start')
@app.route('/prepare_data')
def test_message():
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
    return jsonify({
            "data": most_popular
        })

@app.route('/get_data')
def get_data():
    num = request.args.get('num')
    posts = list()
    with sql.connect('my_db') as con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM posts WHERE group_id=(?)", (num, ))
        posts = cursor.fetchall()
    return jsonify({"data": posts})

if __name__=='__main__':
    app.run()
    # manager.run()
    # socketio.run(app)
