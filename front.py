from flask import Flask, render_template, request,session,logging,flash,url_for,redirect,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os
import secrets

from selenium import webdriver
from getpass import getpass

from flask import Flask, jsonify, request, Response, render_template
from pykafka import KafkaClient
import json

# #twitter analysis
# import sys,tweepy,csv,re
# from textblob import TextBlob
# import matplotlib.pyplot as plt
# #

def get_kafka_client():
    return KafkaClient(hosts='127.0.0.1:9092')


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__,template_folder='template')
app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# this is contact model
class Contact(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Register(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    rno = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80), nullable=False)
    lname=db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(12), nullable=False)
    password2 = db.Column(db.String(120), nullable=False)


@app.route("/")
def home():
    return render_template('index.html',params=params)


@app.route("/login",methods=['GET','POST'])
def login():
    if('email' in session and session['email']):
        return render_template('index1.html',params=params)

    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        
        login = Register.query.filter_by(email=email, password=password).first()
        if login is not None:
            session['email']=email
            return render_template('index1.html',params=params)
        else:
            flash("plz enter right password")
    return render_template('login.html',params=params)
  


@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    return render_template("index1.html",params=params)

@app.route("/register", methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        fname = request.form.get('fname')
        lname =request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if (password==password2):
            entry = Register(fname=fname,lname=lname,email=email,password=password, password2=password2)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("plz enter right password")
    return render_template('register.html',params=params)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    sendmessage=""
    errormessage=""
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        try:
            entry = Contact(name=name, phone_num = phone, message = message, email = email,date= datetime.now() )
            db.session.add(entry)
            sendmessage="Thank you for contacting us !.Your message has been sent."
        except Exception as e:
            errormessage="Error : "+ str(e)
        finally:
             db.session.commit()


    return render_template('contacts.html',params=params ,sendmessage=sendmessage,errormessage=errormessage)
   
@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('home'))


@app.route("/onlineuser")
def onlineuser():
    return(render_template('onlineuser.html'))

@app.route('/topic/<topicname>')
def get_messages(topicname):
    client = get_kafka_client()
    def events():
        for i in client.topics[topicname].get_simple_consumer():
            yield 'data:{0}\n\n'.format(i.value.decode())
    return (Response(events(), mimetype="text/event-stream"))



# @app.route("/sentiment")
# def sentiment():
#     # sa = SentimentAnalysis()
#     # sa.DownloadData()
#     return render_template("sentiment.html", params=params)


from flask import Flask, render_template, abort, request
import sys
from twython import Twython
import nltk
from dictionary import Dictionary

APP_KEY = 'p7vsABTdtzTbLoKUhcPiKn9Gs'
APP_SECRET = 'zKRb7jp3qPh7wBQ5VwM30dZUKL25HSdwx4QNctsVuoNaeRXgr3'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)


class SentimentScore:
    def __init__(self, positive_tweets, negative_tweets, neutral_tweets):

        self.positive_tweets = positive_tweets
        self.negative_tweets = negative_tweets
        self.neutral_tweets = neutral_tweets

        self.neg = len(negative_tweets)
        self.pos = len(positive_tweets)
        self.neut = len(neutral_tweets)




dictionaryN = Dictionary('negative-words.txt')

dictionaryP = Dictionary('positive-words.txt')

def sentiment(tweet):

    negative_score = 0
    positive_score = 0

    tokenizer = nltk.tokenize.TweetTokenizer()
    tweet_words = tokenizer.tokenize(tweet)

    for word in tweet_words:
        negative_score += dictionaryN.check(word)

    for word in tweet_words:
        positive_score += dictionaryP.check(word)

    if negative_score > positive_score:
        return 'negative'
    elif negative_score == positive_score:
        return 'neutral'
    else:
        return 'positive'

    # use dictionary to count negative frequent

def sentiment_analysis(tweets):

    negative_tweets = []
    positive_tweets = []
    neutral_tweets = []

    for tweet in tweets:

        res = sentiment(tweet['text'])

        if res == 'negative':
            negative_tweets.append(tweet['text'])
        elif res == 'positive':
            positive_tweets.append(tweet['text'])
        else:
            neutral_tweets.append(tweet['text'])

    return SentimentScore(positive_tweets, negative_tweets, neutral_tweets)


@app.route("/sentiment", methods=["POST","GET"])
def root():

    if request.method == "POST":

        user_timeline = twitter.get_user_timeline(screen_name=request.form['twitter_username'], count = 100)

        return render_template("result.html", result=sentiment_analysis(user_timeline), username=request.form['twitter_username'])
    else:
        return render_template("sentiment.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    
    app.run(debug=True)
