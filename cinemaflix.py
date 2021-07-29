# import the required library
import re
import numpy as np
from typing_extensions import runtime
from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import json
import requests
from bs4 import BeautifulSoup
import pickle
from collections import Counter

app = Flask(__name__)
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# import the dataset

rf_model = pickle.load(open('random_forest_model_2.pkl', 'rb'))
vec_trans = pickle.load(open('vector_transform.pkl', 'rb'))
file = open('file1.txt', 'r', encoding='utf-8')
text = file.read()


def tokens(word):
    return re.findall(r'[a-z]+', word.lower())


words = tokens(text)
counts = Counter(words)


def correct_word(word):
    pred_word = (known(pred0(word)) or
                 known(pred1(word)) or
                 known(pred2(word)) or
                 [word])
    return max(pred_word, key=counts.get)


def known(word):
    return {w for w in word if w in counts}


def pred0(word):
    return {word}


def pred1(word):
    "Return all strings that are one edit away from this word."
    pairs = splits(word)
    deletes = [a+b[1:] for (a, b) in pairs if b]
    transposes = [a+b[1]+b[0]+b[2:] for (a, b) in pairs if len(b) > 1]
    replaces = [a+c+b[1:] for (a, b) in pairs for c in alphabet if b]
    inserts = [a+c+b for (a, b) in pairs for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def pred2(word):
    return {e2 for e1 in pred1(word) for e2 in pred1(e1)}


def splits(word):
    "Return a list of all possible (first, rest) pairs that comprise word."
    return [(word[:i], word[i:])
            for i in range(len(word)+1)]


alphabet = 'abcdefghijklmnopqrstuvwxyz'


def create_model():
    movie_list = pd.read_csv('movie_list1.csv')

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf = tfidf.fit_transform(movie_list['comb'])

    cosine_similarity = linear_kernel(tfidf, tfidf)
    indices = pd.Series(
        movie_list.index, index=movie_list['original_title']).drop_duplicates()
    return cosine_similarity, indices, movie_list


def get_recommendition(title):
    cosine_simlarity, indices, movie_list = create_model()
    if(title not in movie_list['original_title'].unique()):
        return 'movie not in our database'
    else:
        idx = indices[title]
        sim_scores = list(enumerate(cosine_simlarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:9]
        movie_indices = [i[0] for i in sim_scores]
        mov = []
        for i in movie_indices:
            mov.append(movie_list['original_title'][i])
        return mov


def getting_review(id):
    res = requests.get(
        'https://www.imdb.com/title/{}/reviews/?ref_=tt_ql_urv'.format(id))

    soup = BeautifulSoup(res.text, 'html.parser')
    results = soup.find_all("div", {"class": "text show-more__control"})
    review_list = []
    review_status = []
    for review in results:
        if review.string:
            review_list.append(review.string)
            query = np.array([review.string])
            review_vector = vec_trans.transform(query)
            pred = rf_model.predict(review_vector)
            review_status.append('Good' if pred == 'positive' else 'Bad')

    if len(review_list) > 6:
        reviewed_6 = review_list[:6]
    else:
        reviewed_6 = review_list

    reviewed_dict = {reviewed_6[i]: review_status[i]
                     for i in range(len(reviewed_6))}
    return reviewed_dict


def autocomplet():
    movie_list = pd.read_csv('movie_list.csv')
    return list(movie_list['original_title'])


@app.route('/')
def home_page():
    return render_template('cinemaflix_home.html')


@app.route('/trend_movie', methods=["POST", "GET"])
def trend_movie():
    movie_list_data = autocomplet()
    trend_id = json.loads(request.form["trend_id"])
    trend_title = json.loads(request.form["trend_title"])
    trend_poster = json.loads(request.form["trend_poster"])
    trend_movie_data = {trend_title[i]: trend_poster[i]
                        for i in range(len(trend_poster))}
    return render_template('cinemaflix_main.html', trend_movie=trend_movie_data, movie_list=movie_list_data)


@app.route('/correct', methods=["POST"])
def correct():
    incorrect = request.form["nam"]
    #corrected = correct_word(incorrect)
    corrected = list(map(correct_word, tokens(incorrect)))
    return corrected[0]


@app.route('/correct_movie', methods=["POST"])
def correct_movie():
    corrected_id = json.loads(request.form["corrected_id"])
    corrected_title = json.loads(request.form["corrected_title"])
    corrected_poster = json.loads(request.form["corrected_poster"])
    corrected_desc = json.loads(request.form["corrected_desc"])
    corrected_movie_data = {
        corrected_title[i]: [corrected_poster[i], corrected_desc[i]] for i in range(len(corrected_title))}
    return render_template('cinemaflix_list.html', corrected_movie=corrected_movie_data)


@app.route('/recomend', methods=["POST"])
def recomend():
    title = request.form["name"]
    rec = get_recommendition(title)
    if(type(rec) == type('string')):
        return rec
    else:
        return "--".join(rec)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    movie_title = request.form["movie_title"]
    imdb_id = request.form["imdb_id"]
    overview = request.form["overview"]
    rating = request.form["rating"]
    popularity = request.form["popularity"]
    vote_count = request.form["vote_count"]
    genre = request.form["genre_list"]
    status = request.form["status"]
    release = request.form["release"]
    runtime = request.form["runtime"]
    poster = request.form["poster"]
    rec_movie = request.form["rec_movie"]
    movie_poster = request.form["movie_poster"]

    rec_movie_title = json.loads(rec_movie)
    movie_poster_data = json.loads(movie_poster)
    cast_id = json.loads(request.form["cast_id"])
    cast_name = json.loads(request.form["cast_name"])
    cast_char = json.loads(request.form["cast_char"])
    cast_profile = json.loads(request.form["cast_profile"])
    cast_dob = json.loads(request.form["cast_dob"])
    cast_bio = json.loads(request.form["cast_bio"])
    cast_birthplace = json.loads(request.form["cast_birthplace"])
    poster_arr = movie_poster_data['poster_arr']
    poster_rating = movie_poster_data['poster_rating']
    poster_release = movie_poster_data['poster_release']

    rec_movie_data = {rec_movie_title[i]: [poster_arr[i], poster_rating[i], poster_release[i]]
                      for i in range(len(poster_arr))}
    cast_description = {cast_name[i]: [cast_id[i], cast_profile[i], cast_dob[i],
                                       cast_bio[i], cast_birthplace[i]] for i in range(len(cast_birthplace))}
    cast_details = {cast_name[i]: [
        cast_id[i], cast_char[i], cast_profile[i], cast_dob[i]] for i in range(len(cast_profile))}
    print(movie_title)

    reviewed_dic = getting_review(imdb_id)

  # html_str = '<a href="#" class="read_more">Read More</a><span class="more_text">'
  # updated_review = []
  # for rev in reviewed_6:
  #     if len(rev) > 100:
  #         rev1 = rev[:100]+html_str+rev[100:]
  #         updated_review.append(rev1+'</span>')
  #     else:
  #         updated_review.append(rev)

    return render_template('cinemaflix_detail.html', title=movie_title, overview=overview, rating=rating, popularity=popularity, vote_count=vote_count, genre=genre, status=status, release=release, runtime=runtime, poster=poster, movie_poster_data=rec_movie_data, cast_details=cast_details, cast_description=cast_description, review=reviewed_dic)


if __name__ == '__main__':
    app.run(debug=True)
