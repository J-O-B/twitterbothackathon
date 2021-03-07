import os
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from flask_pymongo import PyMongo
from flask import (
    Flask, render_template,
    redirect, request, session, url_for)
from datetime import datetime as dt
from credentials import *
import json
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = ("mongodb+srv://test:test1988@clustertweet.cfvo1.mongodb.net/theythinkitsallclover?retryWrites=true&w=majority")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Override the Std Class
# (https://www.kite.com/python/docs/examples.streaming.StdOutListener)
class StdOutListener(StreamListener):
    # https://www.kite.com/python/docs/tweepy.streaming.StreamListener.on_data
    def on_data(self, data):
        text = json.loads(data)
        content = text["text"]
        username = text["user"]['name']
        avatar = text["user"]["profile_image_url"]
        url = f'https://twitter.com/{text["user"]["screen_name"]}'
        time_posted = dt.strptime(text["created_at"],
                                  '%a %b %d %H:%M:%S %z %Y')
        try:
            if (text["place"]["bounding_box"]["coordinates"]):
                coordinates = text["place"]["bounding_box"]["coordinates"]
                location = coordinates[0][0]
            else:
                location = text["user"]["location"]
        except:
            location = "No Location"
        tweet_data = {
                "content": content,
                "username": username,
                "avatar": avatar,
                "url": url,
                "location": location,
                "time_posted": time_posted
            }
        print(tweet_data)
        mongo.db.tweets.insert_one(tweet_data)


if __name__ == "__main__":
    auth = OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    # Listen for a stream
    listen = StdOutListener()
    stream = Stream(auth, listen)
    # Filter the stream to tweets containing #theyThinkItsAllClover:
    stream.filter(track=['#theyThinkItsAllClover'])
