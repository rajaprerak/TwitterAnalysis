from TweetAnalysis.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, \
    TWITTER_ACCESS_SECRET, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET_KEY, TMDB_API_KEY, TMDB_LANGUAGE, NUMBER_OF_MOVIES, \
    DATE_SINCE, NUMBER_OF_SONGS_TWEETS, NUMBER_OF_SONGS, BASE_DIR, PROJECT_ID, TOPIC_ID
import tweepy
from TweetAnalysis.sentiment import get_tweet_sentiment
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tmdbv3api import TMDb, Trending
import requests, shutil
import os
import time
import json
from google.cloud import pubsub_v1
from datetime import date, datetime
import random
from pytz import timezone
tz = timezone('MST')

path = os.getcwd()
# parent_dir = os.path.abspath(os.path.join(path, os.pardir))
cc_proj_key_path = os.path.join(path, "cc-project-2-key.json")
# f = open(cc_proj_key_path)
# print(f)

print(cc_proj_key_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cc_proj_key_path

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def init_api():
    # Twitter API's setup:
    # auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    # Replace the API_KEY and API_SECRET with your application's key and secret.
    auth = tweepy.AppAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    # api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    tw = tweepy.API(auth)

    # Spotify API setup
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                          client_secret=SPOTIFY_CLIENT_SECRET_KEY)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # TMDB API setup
    tmdb = TMDb()
    tmdb.api_key = TMDB_API_KEY
    tmdb.language = TMDB_LANGUAGE

    return tw, sp, tmdb

def get_trending_movie_names():
    tw, sp, tmdb = init_api()
    trend = Trending()
    movie_week = trend.movie_week()
    movie_names = []
    movie_week = movie_week[:NUMBER_OF_MOVIES]
    for m_dict in movie_week:
        movie_name = m_dict.original_title
        movie_names.append(movie_name)
    return movie_names

def get_trending_movie_sentiments():
    tw, sp, tmdb = init_api()
    trend = Trending()
    movie_week = trend.movie_week()
    movies_tweets = {}
    movie_week = movie_week[:NUMBER_OF_MOVIES]
    for m_dict in movie_week:
        movie_name = m_dict.original_title

        image_url = 'https://image.tmdb.org/t/p/original'+m_dict.poster_path
        filename = movie_name + '.jpg'
        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True

        dir_path = os.path.join(BASE_DIR, 'twitter', 'images', 'movies')
        image_path = os.path.join(dir_path, filename)

        # if not os.path.exists(dir_path):
        #     os.makedirs(dir_path)

        # with open(image_path,'wb') as f:
        #     shutil.copyfileobj(r.raw, f)

        tweets = tweepy.Cursor(tw.search,
                               q=movie_name,
                            #    result_type="recent",
                               lang="en",
                               since=DATE_SINCE,
                               tweet_mode='extended').items(NUMBER_OF_SONGS_TWEETS)
        
        tweet_text = []
        for tweet in tweets:
            tweet_extended = tweet.retweeted_status.full_text if tweet.full_text.startswith("RT @") else tweet.full_text
            user_image = "https://bootdey.com/img/Content/avatar/avatar"+str(random.randint(1,8))+".png"
            tweet_text.append((tweet_extended, get_tweet_sentiment(tweet_extended),tweet.author.name, user_image))
            d = datetime.now(tz)
            output = {"name":movie_name,"tweet":tweet_extended,"sentiment":get_tweet_sentiment(tweet_extended),"category":"movie","date":str(d.date())}
            pubsub_output = json.dumps(output)
            data = str(pubsub_output)
            publisher.publish(topic_path, data.encode("utf-8"))

        movies_tweets[movie_name] = tweet_text
        
    return movies_tweets

def get_trending_song_names():
    tw, sp, tmdb = init_api()
    result = sp.new_releases(country='US', limit=NUMBER_OF_SONGS, offset=0)
    song_names = []
    for each in result['albums']['items']:
        song_name = each['name']
        song_names.append(song_name)
    return song_names

def get_trending_songs_sentiments():
    tw, sp, tmdb = init_api()
    # Get new releases from spotify
    result = sp.new_releases(country='US', limit=NUMBER_OF_SONGS, offset=0)
    songs_tweets = {}
    for each in result['albums']['items']:
        song = each['name']
        artist = each['artists'][0]['name']
        search_words = song + ' ' + artist

        image_url = each['images'][0]['url']
        filename = song +' By ' + artist + '.jpg'
        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True

        dir_path = os.path.join(BASE_DIR, 'twitter', 'images', 'songs')
        image_path = os.path.join(dir_path, filename)

        # if not os.path.exists(dir_path):
        #     os.makedirs(dir_path)
        #
        # with open(image_path,'wb') as f:
        #     shutil.copyfileobj(r.raw, f)
        tweets = tweepy.Cursor(tw.search,
                               q=search_words,
                            #    result_type="recent",
                               lang="en",
                               since=DATE_SINCE,
                               tweet_mode='extended').items(NUMBER_OF_SONGS_TWEETS)

        tweet_text = []
        for tweet in tweets:
            tweet_extended = tweet.retweeted_status.full_text if tweet.full_text.startswith("RT @") else tweet.full_text
            user_image = "https://bootdey.com/img/Content/avatar/avatar"+str(random.randint(1,8))+".png"
            tweet_text.append((tweet_extended, get_tweet_sentiment(tweet_extended), tweet.author.name, user_image))
            d = datetime.now(tz)
            output = {"name":search_words,"tweet":tweet_extended,"sentiment":get_tweet_sentiment(tweet_extended),"category":"song","date":str(d.date())}
            pubsub_output = json.dumps(output)
            data = str(pubsub_output)
            publisher.publish(topic_path, data.encode("utf-8"))
        songs_tweets[search_words] = tweet_text
        
    return songs_tweets

    
def test_autoscaling():

    movies_tweets = {}
    movie_names_all = ['Mortal Kombat','Godzilla vs. Kong','Nobody','Stowaway','Nomadland']
    movie_tweets_all = [['Fans of the Mortal Kombat games hearing “Flawless Victory” in the movie. https://t.co/gPKUAbg3y8', 'Fans of the Mortal Kombat games hearing “Flawless Victory” in the movie. https://t.co/gPKUAbg3y8', 'Fans of the Mortal Kombat games hearing “Flawless Victory” in the movie. https://t.co/gPKUAbg3y8', 'The boys and I are sitting down to record tonight! Tune in to hear our thoughts about Remedy Entertainment’s Control and the Mortal Kombat movie. Also, @FlippingTheNerd is going to have a fun story!!! https://t.co/XImNcC2636', "I know it's the #NFLDraft but can we all take a moment to pause, take a deep breath, and talk about how bad the new Mortal Kombat movie was?"], ['Godzilla vs. Kong Release Date, Review, Trailer, Tickets, Cast, and More - Gadget Informer @ https://t.co/Zm0wcCkIA2 https://t.co/3qAccY87pG', "@Tiff_SunnySouth @samba_tv @getFANDOM Mortal Kombat is not bigger than Godzilla vs Kong...I'd like it to be...but it isn't", 'Hollow Earth unused Titan Shimida explained in Godzilla vs. Kong Art Book! (PREVIEW) #Godzilla #GodzillaVsKong https://t.co/diQsXwL1qu', 'Barca atleti will be the real Kong vs Godzilla.', '@Ayodelebiodun Okay lets go\n\nNOBODY\nYING YANG MASTER\nGODZILLA VS KONG\nHONEST THIEF\nLOST BULLET\nRAYA AND THE LAST DRAGON (ANIMATION)\nVIRTUOSO\n6 UNDERGROUND a bit old but not bad at all'], ['nobody:\nedward in biology class: https://t.co/RuBg1wO3GK', "oh no I'm offering $9 an hour and nobody is applying to be my heckin workerino", 'nobody:\n\nwilbur soot: https://t.co/Eg6KIQnVEn', 'nobody:\nedward in biology class: https://t.co/RuBg1wO3GK', '@HawleyMO Nobody wants it!!!!'], ['I’m watching stowaway and thinking @josh_dobbs1 would’ve save the whole ship and not even broken a sweat', 'I just watched stowaway, what an absolutely beautiful movie! #StowawayMovie', '@Sports_Doctor2 Stowaway', '@yungkay____ 😂 I haven’t seen it. Have you seen Stowaway, it was really good but I’m just like what happens next ???', 'I just watched Stowaway (2021) https://t.co/lXQ7gzme4P #trakt'], ["An understandable story, but 115 degrees will curtail demand. Quartzsite, Arizona, made famous by Oscar-winner 'Nomadland,' readies for new tourists https://t.co/N6Vt3YW16M via @azcentral", 'Western media frames China as passing on a soft power opportunity gifted by the West, while it pushes 500 pieces of anti-China propaganda in last 48 hrs about this story.\nhttps://t.co/Wlj4ivxdXb', 'Chloé Zhao talks about her massively ambitious Marvel movie #Eternals, starring Angelina Jolie, Salma Hayek, Richard Madden, Kit Harington, Brian Tyree Henry and Kumail Nanjiani. The film also features the MCU’s first LGBTQ and deaf superheroes. https://t.co/pkzLcuWOdU https://t.co/nDQm6m4rha', '@elazarcultural @NextBestPicture Way too many 10s and lol @ Nomadland!', 'Chloé Zhao talks about her massively ambitious Marvel movie #Eternals, starring Angelina Jolie, Salma Hayek, Richard Madden, Kit Harington, Brian Tyree Henry and Kumail Nanjiani. The film also features the MCU’s first LGBTQ and deaf superheroes. https://t.co/pkzLcuWOdU https://t.co/nDQm6m4rha']]
    movie_users_all = [['“Panda is Not a Panda “', 'J🇸🇻', 'earthsdoormat🌎🌈✌🏾', 'Horror Fan Ryan👻💀🧟\u200d♂️🎃🎃', 'Drew Bee'], ['NewsVerses', 'George Elliott', '若年寄YoungJijeyヤングジジィ', 'Tororo Penrenren', 'Westsyde Bwoi'], ['ellie', "Im Kramp'd again", 'warmp', 'H.Gray™ - Jared Lexo', 'jtve'], ['JOE-NATEX', 'Vii', 'Miss Nurah', '🔪', 'petermesh'], ['Charles Danville', 'mywang999', 'Helmet of Salvation', 'Obama, Onika, Omari', 'Carol Chrispim']]
    
    for i in range(len(movie_names_all)):

        movie_name = movie_names_all[i]
        tweet_text = []
        for j in range(len(movie_tweets_all[i])):
            tweet_extended = movie_tweets_all[i][j]
            user_image = "https://bootdey.com/img/Content/avatar/avatar"+str(random.randint(1,8))+".png"
            tweet_text.append((tweet_extended, get_tweet_sentiment(tweet_extended),movie_users_all[i][j], user_image))
            d = datetime.now(tz)
            output = {"name":movie_name,"tweet":tweet_extended,"sentiment":get_tweet_sentiment(tweet_extended),"category":"movie","date":str(d.date())}
            pubsub_output = json.dumps(output)
            data = str(pubsub_output)
            publisher.publish(topic_path, data.encode("utf-8"))

        movies_tweets[movie_name] = tweet_text
        movie_tweets_all.append(tweet_text)

    return movies_tweets