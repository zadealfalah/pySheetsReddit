import os
from dotenv import load_dotenv
import praw
import pygsheets
import datetime as dt
import spacy


load_dotenv()
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
username = os.getenv("user")
password = os.getenv("password")
user_agent = os.getenv("user_agent")
secretpath = os.getenv("secret_path")  # For google client secrets json file
sheetName = os.getenv("sheet_name")  # Sheet to use
commentWksName = os.getenv("comment_workshet_name")  # Worksheet within the sheet to use to store comments
nerWksName = os.getenv("ner_worksheet_name")  # Worksheet within the sheet to use to store NER info

subredditsToUse = os.getenv("subreddits")  # space separated list of subreddits to look through
subredditsToUse = subredditsToUse.split()  # Turns the os values into a list used later on
timeframe = os.getenv("timeframe")  # Timeframe you wish to use e.g. 'weeks', 'days', etc
timeInt = os.getenv("timeInt")  # number of timeframes you wish to use e.g. a 2 here with timeframe == 'weeks' uses 2 weeks of data
numberOfPosts = os.getenv("num_posts")  # Number of posts you want to look at, at most, for each subreddit

# creating an authorized reddit instance
def login(client_id, client_secret, username, password, user_agent):
    reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)
    return reddit

reddit = login(client_id, client_secret, username, password, user_agent)

secretsPath = secretpath  # client secret from google as a json
gc = pygsheets.authorize(outh_file=secretsPath)
sh = gc.open(sheetName)
wks = sh.worksheet_by_title(commentWksName)  # Comment storage worksheet
nerWks = sh.worksheet_by_title(nerWksName)  # NER storage worksheet

def cleanSheetByTime(clientToUse=gc, sheetToUse=sh, wksToUse=wks):
    """
    Function to clean a given worksheet by the timeCreated column.  This function uses the clientToUse 
    pygsheets client to look at the wksToUse worksheet within the sheetToUse spreadsheet.
    It then removes any rows where the timeCreated column shows a post is from more than a week ago.
    
    Args:
        clientToUse (pygsheets.client.Client): the pygsheets client we'll be using
        sheetToUse (pygsheets.spreadsheet.Spreadsheet): the pygsheets spreadsheet we'll be cleaning in
        wksToUse (pygsheets.worksheet.Worksheet): the worksheet we'll be cleaning
    """
    cells = wksToUse.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')  
    timeNow = dt.datetime.now()
    cutoffTime = timeNow - dt.timedelta(**{timeframe : timeInt})  # Set the cutoff time
    rowsToDelete = [i+2 for i, r in enumerate(cells[1:]) if (dt.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")  <=  cutoffTime)]  # i+2 as 1 for removing 1st row of cells and another for sheets counting from 1 instead of 0

    # reqs just tells batch_update which rows to delete using the API wrapper
    reqs = [
    {
        "deleteDimension": {
            "range": {
                "sheetId": wksToUse.id,
                "startIndex": e-1,
                "endIndex": e,
                "dimension": "ROWS",
            }
        }
    }
    for e in rowsToDelete
    ]
    reqs.reverse()
    clientToUse.sheet.batch_update(sheetToUse.id, reqs)
    
    
def updatePosts(subList=subredditsToUse, timeFilter=timeframe, setLimit=numberOfPosts, wksToUse=wks, rInstance=reddit): 
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
    for subr in subList:
        subrInstance = rInstance.subreddit(subr)
        firstCellCheck = wksToUse.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')  
        currentIDs = [r[6] for i, r in enumerate(firstCellCheck[1:])]  # Get list of all current post IDs in our sheet
        for submission in subrInstance.top(time_filter=timeFilter, limit=setLimit):
            if submission.id in currentIDs:  # Don't repeat posts!
                continue
            else:
                d = {}
                d['timeCreated'] = dt.datetime.fromtimestamp(submission.created_utc)
                d['subreddit'] = str(submission.subreddit.display_name)
                d['title'] = str(submission.title)
                d['score'] = int(submission.score)
                d['author'] = str(submission.author.name)
                d['selftext'] = str(submission.selftext)
                d['id'] = str(submission.id)
                # dfToUse = pd.concat([dfToUse,pd.DataFrame.from_dict(d, orient='index').T], ignore_index=True, axis=0)
                
                cells = wksToUse.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')  
                lastrow = len(cells)  # Must update every time so as to properly append rows
                
                # make the timeCreated json serializable for appending to worksheet
                dvals = list(d.values())
                dvals[0] = dvals[0].isoformat()
                
                
                wksToUse.insert_rows(lastrow, number=1, values=dvals)
        
        
def getNER(sourceWks=wks, nerWks=nerWks):

    df = sourceWks.get_as_df()  # Get the postInfo worksheet as a dataframe
    
    firstCellCheck = nerWks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')  
    currentIDs = [r[0] for i, r in enumerate(firstCellCheck[1:])]  # Get list of all current post IDs in our sheet
    
    NER = spacy.load("en_core_web_sm")
    for i, row in df.iterrows():
        if row['id'] in currentIDs:  # Don't repeat work!
            continue
        else:
            d = {}
            d['postID'] = str(row['id'])
            nerText = NER(row['title'] + " " + row['selftext'])
            for word in nerText.ents:
                d['nerWord'] = str(word.text)
                d['nerLabel'] = str(word.label_)
                cells = nerWks.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')  
                lastrow = len(cells)
                dvals = list(d.values())
                nerWks.insert_rows(lastrow, number=1, values=dvals)
                

cleanSheetByTime()
updatePosts()
getNER()