import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
import praw
import datetime as dt
import mysql.connector
from mysql.connector import errorcode
import spacy

load_dotenv(override=True)
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
username = os.getenv("user")
password = os.getenv("password")
user_agent = os.getenv("user_agent")
secretpath = os.getenv("secret_path")  # For google client secrets json file
sheetName = os.getenv("sheet_name")  # Sheet to use
commentWksName = os.getenv("comment_workshet_name")  # Worksheet within the sheet to use to store comments
nerWksName = os.getenv("ner_worksheet_name")  # Worksheet within the sheet to use to store NER info

subredditsToUse = os.getenv("subredditsToUse")  # space separated list of subreddits to look through
subredditsToUse = subredditsToUse.split()  # Turns the os values into a list used later on
timeframe = os.getenv("timeframe")  # Timeframe you wish to use e.g. 'weeks', 'days', etc
timeInt = os.getenv("timeInt")  # number of timeframes you wish to use e.g. a 2 here with timeframe == 'weeks' uses 2 weeks of data
numberOfPosts = os.getenv("num_posts")  # Number of posts you want to look at, at most, for each subreddit

mysqluser = os.getenv("mysqluser")
mysqlpassword = os.getenv("mysqlpassword")
mysqlhost = os.getenv("mysqlhost")
mysqldatabase = os.getenv("mysqldatabase")

def login(client_id, client_secret, username, password, user_agent):
    reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)
    return reddit


def updatePosts(subList=subredditsToUse, timeFilter=timeframe, setLimit=numberOfPosts, rInstance=reddit): 
    """
    Function to update the google worksheet we are using.  
    This function goes through each subreddit in subList individually so as to get top posts for each subreddit rather than their combined subreddit object
    
    Args:
        subList (list): list of all subreddits to iterate over
        timeFilter (str): length of time to look through top posts.  Possible options of 'hour', 'day', 'week', 'month'
        setLimit (int): number of top posts to look at within the timeframe
        dfToUse (dataframe): the dataframe we will put our submission data into for further use
        wksToUse (pygsheets.worksheet.Worksheet): the worksheet we'll be updating
        rInstance (praw.reddit.Reddit): the reddit instance we'll be using to extract posts
    """
    add_post = ("INSERT INTO postinfo "
            "(id, author, score, title, subreddit, timecreated) "
            "VALUES (%s, %s, %s, %s, %s, %s)")
    
    cnx = mysql.connector.connect(user=mysqluser, password=mysqlpassword,
                            host=mysqlhost, database=mysqldatabase)
    cursor = cnx.cursor()
    for subr in subList:
        subrInstance = rInstance.subreddit(subr)
        for submission in subrInstance.top(time_filter=timeFilter, limit=setLimit):
            try: 
                data_post = (str(submission.id), str(submission.author), int(submission.score), 
                             str(submission.title), str(submission.subreddit.display_name), 
                             dt.datetime.fromtimestamp(submission.created_utc))
                cursor.execute(add_post, data_post)
                cnx.commit()
            except:  # Cannot excplitly except an IntegrityError in python
                continue
    
    cursor.close()
    cnx.close()
    
    
def getNER():
    add_ner = ("INSERT INTO nerinfo "
           "(nerword, nerlabel, postid) "
           "VALUES (%s, %s, %s)")
    
    NER = spacy.load("en_core_web_sm")
    cnx = mysql.connector.connect(user=mysqluser, password=mysqlpassword,
                            host=mysqlhost, database=mysqldatabase)
    cursor = cnx.cursor()
    query = ("SELECT id FROM nerinfo")
    cursor.execute(query)
    currentIDs = []  # bucket to hold all IDs of posts which have already had NER analysis done before this call of getNER()
    cursor.close()
    for nerID in cursor:
        currentIDs.append(nerID[0])

    cursor = cnx.cursor()
    query = ("SELECT id, title FROM postinfo WHERE id NOT IN %(currentIDs)s")
    cursor.execute(query)
    cursor.close()
    
    cursor = cnx.cursor() 
    for id, title in query:
        try:
            nerText = NER(title)
            for word in nerText.ents:
                ner_post = (str(word.text), str(word.label_), str(id))
                cursor.execute(add_ner, ner_post)
        except: #Cannot excplitly except an IntegrityError in python
            continue
    cursor.close()
    cnx.close()


reddit = login(client_id, client_secret, username, password, user_agent)
updatePosts()
getNER()