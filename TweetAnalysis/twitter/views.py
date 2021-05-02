from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.shortcuts import HttpResponse

from django.http import JsonResponse
from twitter.controller import get_trending_movie_sentiments, get_trending_songs_sentiments, get_trending_movie_names, get_trending_song_names, test_autoscaling
from collections import defaultdict
# Create your views here.
def index(request):
    if len(request.GET) > 0:
        email =request.GET.get('user_email')
        print(email)
        movies_names = get_trending_movie_names()
        songs_names = get_trending_song_names()
        context = {
            'movies_names': movies_names,
            'songs_names': songs_names
        }
        msg_str = ""
        for idx, movie in enumerate(movies_names):
            if idx == 0:
                msg_str += "Trending Movies: \n"
                msg_str += f"{idx+1}.) {movie}\n"
            else:
                msg_str += f"{idx+1}.) {movie}\n"

        msg_str += "\n"
        for idx, song in enumerate(songs_names):
            if idx == 0:
                msg_str += "Trending Songs: \n"
                msg_str += f"{idx+1}.) {song}\n"
            else:
                msg_str += f"{idx+1}.) {song}\n"


        subject = "Trending List"
        # message = "simple plain text"
        html_message = ""
        from_email = ""
        recipient_list = []
        recipient_list.append(email)
        send_mail(subject, message=msg_str, from_email=None, recipient_list=recipient_list,
                  fail_silently=False, html_message=None)
        return render(request, 'twitter/index.html', context=context)

    movies_names = get_trending_movie_names()
    songs_names = get_trending_song_names()

    context = {
        'movies_names': movies_names,
        'songs_names': songs_names
    }
    return render(request, 'twitter/index.html', context=context)

    # return JsonResponse(movies_tweets)


def movies(request):
    movies_tweets = get_trending_movie_sentiments()
    context = {
        'movies_tweets': movies_tweets,
    }
    if len(request.GET) > 0:
        email =request.GET.get('user_email')
        print(email)
        movies_posi_tweets_cnt = defaultdict(int)
        for movie, data_list in movies_tweets.items():
            for data in data_list:
                if data[1] == 'positive':
                    movies_posi_tweets_cnt[movie] += 1

        sorted_list = sorted(movies_posi_tweets_cnt, key=lambda x: movies_posi_tweets_cnt[x], reverse=True)[:2]
        msg_str = ""
        for idx, movie in enumerate(sorted_list):
            if idx == 0:
                msg_str += "Trending movies with highest percentage of positive reviews: \n"
                msg_str += f"{idx+1}.) {movie}\n"
            else:
                msg_str += f"{idx+1}.) {movie}\n"

        subject = "Trending List"
        # message = "simple plain text"
        html_message = ""
        from_email = ""
        recipient_list = []
        recipient_list.append(email)
        send_mail(subject, message=msg_str, from_email=None, recipient_list=recipient_list,
                  fail_silently=False, html_message=None)
        return render(request, 'twitter/movies.html', context=context)
    return render(request, 'twitter/movies.html', context=context)


def songs(request):
    songs_tweets = get_trending_songs_sentiments()
    context = {
        'songs_tweets': songs_tweets,
    }
    if len(request.GET) > 0:
        email =request.GET.get('user_email')
        print(email)
        songs_posi_tweets_cnt = defaultdict(int)
        for song, data_list in songs_tweets.items():
            for data in data_list:
                if data[1] == 'positive':
                    songs_posi_tweets_cnt[song] += 1

        sorted_list = sorted(songs_posi_tweets_cnt, key=lambda x: songs_posi_tweets_cnt[x], reverse=True)[:2]
        msg_str = ""
        for idx, song in enumerate(sorted_list):
            if idx == 0:
                msg_str += "Trending songs with highest percentage of positive reviews: \n"
                msg_str += f"{idx+1}.) {song}\n"
            else:
                msg_str += f"{idx+1}.) {song}\n"

        subject = "Trending List"
        # message = "simple plain text"
        html_message = ""
        from_email = ""
        recipient_list = []
        recipient_list.append(email)
        send_mail(subject, message=msg_str, from_email=None, recipient_list=recipient_list,
                  fail_silently=False, html_message=None)
        return render(request, 'twitter/songs.html', context=context)
    return render(request, 'twitter/songs.html', context=context)

def autoscaling(request):
    movies_tweets = test_autoscaling()
    context = {
        'movies_tweets':movies_tweets,
    }
    return render(request, 'twitter/movies.html', context=context)


def send_mail_to_user(request):
    subject = "Hello"
    message = "simple plain text"
    html_message = ""
    from_email = ""
    recipient_list = [""]
    send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, html_message=None)
    return HttpResponse(f"mail sent")
    # return redirect(request, "twitter/index.html", context=None)
