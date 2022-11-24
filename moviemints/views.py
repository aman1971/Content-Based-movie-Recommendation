from django.shortcuts import render
from .models import MovieData, MovieIndices
from django.core.files.storage import FileSystemStorage
import pandas as pd
import numpy as np
import requests
import logging
from bs4 import BeautifulSoup
from django.http import HttpResponse
import pickle as pkl

# Create your views here.

# <------Home Page view----->
def home(request):
    api = '1a2d51b966ece85423555707eb93beaf'
    url = "https://api.themoviedb.org/3/trending/all/day?"
    PARAMS = {'api_key':api}
    try:
        movie_name = MovieData.objects.all().values('movie_name')

        trend_data = requests.get(url=url,params= PARAMS)
        trend_data = trend_data.json()
        trend_details = []
        print(len(trend_data['results']))
        for i in range(20):
            trend_dict = {'trend_id':trend_data['results'][i]['id'], 'trend_title':trend_data['results'][i]['id'], 
                    'trend_poster':f"https://www.themoviedb.org/t/p/w600_and_h900_bestv2/{trend_data['results'][i]['poster_path']}"}
            trend_details.append(trend_dict)
        context = {'trend_details':trend_details, 'movie_name':movie_name}
        return render(request,'moviemints/home.html', context)
    except Exception as Argument:
        logging.exception('error at tranding')
        return render(request,'moviemints/home.html')

# <------End Home Page view----->


# <------Start Movie_list Page view----->

def movie_list(request):
    movie_name = request.GET.get('movie_name')
    try:
        movie_name_list = MovieData.objects.filter(movie_name__icontains=movie_name).values('movie_id','movie_name', 'overview', 'poster_url')
        context = {'movie_name_list':movie_name_list}
        return render(request,'moviemints/movielist.html', context)
    except Exception as Argument:
        logging.exception('error at movie_list')
        return render(request,'moviemints/movielist.html')

# <------End Movie_list Page view----->


# <------Start Movie_detail Page view----->
def movie_detail(request,id):
    cast_details = []
    api = '1a2d51b966ece85423555707eb93beaf'
    url = f"https://api.themoviedb.org/3/movie/{id}/credits?"
    PARAMS = {'api_key':api}
    try:
        cast_data = requests.get(url=url,params= PARAMS)
        cast_data = cast_data.json()
        cast_len = len(cast_data['cast'])
        cast_len = cast_len if cast_len<10 else 10
        for i in range(cast_len):
            cast_detail = {'cast_id':cast_data['cast'][i]['id'], 'cast_name':cast_data['cast'][i]['name'],
                            'cast_char':cast_data['cast'][i]['character'], 'cast_profile': f"https://image.tmdb.org/t/p/original{cast_data['cast'][i]['profile_path']}"}
            cast_details.append(cast_detail)
    except Exception as Argument:
        logging.exception('error at cast_detail')
    
    trailer_url = f"https://api.themoviedb.org/3/movie/{id}/videos?"

    try:
        trailer_detail = requests.get(url=trailer_url,params= PARAMS)
        trailer_detail = trailer_detail.json()
        trailer_key = trailer_detail['results'][0]['key']
    except Exception as Argument:
        logging.exception('error at trailer_key')


    try:
        movie_details = MovieData.objects.get(movie_id=id)

        recommended_movie = get_recommendation(movie_details.movie_name)
        recommended_movie = {'first_5':recommended_movie[:5],'last_5':recommended_movie[5:]}

        review_list = get_review(movie_details.movie_imdb_id)
        review_list = {'first_5':review_list[:3], 'last_5':review_list[3:]}

        context = {'movie_details':movie_details,'cast_details':cast_details, 'recommended_movie':recommended_movie, 'review_list':review_list, 'trailer_key':trailer_key}
        return render(request,'moviemints/moviedetail.html', context)
    except Exception as Argument:
        logging.exception('error at movie_detail')
        return render(request,'moviemints/moviedetail.html')

# <------End Movie_detail Page view----->


# Top 10 Moving recommendation
def get_recommendation(title):
    with open('./media/saved_models/cos_sim', 'rb') as f:
        cos_sim = pkl.load(f)
    
    with open('./media/saved_models/tf_idf', 'rb') as f:
        tf_idf = pkl.load(f)

    tmdb = MovieData.objects.get(movie_name=title)
    tmdb = tmdb.movie_id
    idx = MovieIndices.objects.get(movie_id = tmdb)
    idx = idx.movie_index
    sim_scores = list(enumerate(cos_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:9]
    movie_indices = [i[0] for i in sim_scores]
    mov = []
    for i in movie_indices:
        movie = MovieIndices.objects.get(movie_index=i)
        movie = MovieData.objects.get(movie_id=movie.movie_id)
        movie = {'movie_id':movie.movie_id, 'movie_name':movie.movie_name, 'movie_poster':movie.poster_url}
        mov.append(movie)
    return mov


def get_review(imdb_id):
    with open('./media/saved_models/random_forest_model.pkl', 'rb') as f:
        rf_model = pkl.load(f)
    
    with open('./media/saved_models/vector_transform.pkl', 'rb') as f:
        vec_trans = pkl.load(f)

    res = requests.get(
        'https://www.imdb.com/title/{}/reviews/?ref_=tt_ql_urv'.format(imdb_id))

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

    reviewed_list = []
    for i in range(len(reviewed_6)):
        reviewed_dict = {'review':reviewed_6[i], 'review_status': review_status[i]}
        reviewed_list.append(reviewed_dict)

    return reviewed_list
    # reviewed_dict = {reviewed_6[i]: review_status[i]
    #                  for i in range(len(reviewed_6))}
    # return reviewed_dict
