# pySheetsReddit
Automating Tableau output with Python, Google, and MySQL

## Table of Contents
* [General Info](#general-info)
* [Current Features](#curent-features)
* [Automate Your Own](#automate-your-own)
* [To Do](#to-do)
* [Future Features?](#future-features?)

## General Info
This project seeks to automatically generate and update a public Tableau dashboard with data pulled from Reddit.  It is currently set to look at the 'news', 'nottheonion', 'inthenews', and 'offbeat' subreddits (selected due to being suggested news subreddits).  The code is set to update the data daily and to keep data from up to one week in the past.  This may change based on costs.  

Linked [here](https://public.tableau.com/app/profile/zade.alfalah/viz/pySheetsReddit/Dashboard1?publish=yes) is an example Tableau dashboard which can be automatically updated via the pySheets.py file.

## Current Features
Currently, the data is taken from Reddit using PRAW and pushed into Google Sheets.  The data includes the time a post was created, the subreddit it was created on, as well as the title, self text, author, score, and ID of the post.  The subreddits that these are taken from can be set manually along with the total number of 'top' posts from each subreddit to take.  By default, it takes the top 100 posts within the last week from the 'test' subreddit.  This is all done in the **updatePosts()** function.

Another function called **getNER()** takes the data from **updatePosts()** and performs NER with spaCy on the titles and self texts of the posts then adds this information to different Google worksheet.  

Finally, a function called **cleanSheetByTime()** cleans a given worksheet by batch removing all rows that are outside of our time of interest.

Instead of using Google Sheets there is also the option of using MySQL.

## Automate Your Own
### Step 1: Perparation and Authentication 
You must [authorize](https://pygsheets.readthedocs.io/en/stable/authorization.html) pygsheets to work on your Google Sheets.  You must also set up a [Tableau](https://public.tableau.com/app/discover) and reddit account.  The [requirements.txt](https://github.com/zadealfalah/pySheetsReddit/blob/main/requirements.txt) file can be used to install the necessary Python packages.  The Google Sheet you intend to use should be labled with columns 'timeCreated', 'subreddit', 'title', 'score', 'author', 'selftext', and 'id'.   If you are using MySQL instead of google sheets, you must create and connect your MySQL tables in place of the Google Sheets work.
### Step 2: Setting Your Env
There are quite a few paramters to put in for personal use cases and these are handled via a .env file.  An example .env can be found above labeled as [exampleENV.txt](https://github.com/zadealfalah/pySheetsReddit/blob/main/exampleENV.txt).  Reddit login credentials are stored as text.  Google credentials are by default kept in a google client_secret_..._.json file.  The 'choosing your data' section is where you choose exactly what data you want to keep in your Google Drive.  'subredditsToUse' is a list of the subreddits you would like to use, separated by spaces.  'timeframe' and 'timeInt' are used in [dt.timedelta(timeframe=timeInt)](https://docs.python.org/3/library/datetime.html).  'numberOfPosts' sets the max number of top posts you want to look at per subreddit.  
### Step 3: Running the .py File
Now that you have everything prepared and your data pre-selected you can run the pySheets.py file which will build your Google Sheets.  Or in the case of using MySQL, you would run pySheetsMySQL.py instead. Note that this may take quite some time if you have a large number of subreddits to look through, or a large number of posts to look at per subreddit.  Less popular subreddits could run faster as they may not have the full max number of posts available to look through in the first place.  Regardless, performing NER on every title becomes computationally expensive.
### Step 3.5 - Optional: Automating .py File With Cron or Windows Scheduler
If you wish to have this be completely automatic, you should at this point schedule the file to be run automatically with e.g. cron or Windows Task Scheduler.  An example cron option that was used for a short while on my end would be 59 23 * * 6  to automatically update every Saturday night.
### Step 4: Bulding and Publishing Your Dashboard
Your data is all in place now, so all that is left to do is to connect your Tableau to your Google Drive (or MySQL database) and format your dashboard to showcase whatever it is you care about in the data!
Note that Tableau is stopping Google Sheets connectivity so it is requisite that your file be in your Google Drive starting in around April, 2023.  Once you have your dashboard formatted how you want it, you can set your data to automatically update from the Google Drive and you are all good to publish!
### Step 5: Admire Your Work
You now have a fully automated (should you have completed step 3.5) Tableau dashboard showing whatever it is that you want to show about the subreddits in question.  No more work is required unless you want to change something in which case you need only follow these 5 steps again - and this time you won't even have to re-authenticate!


## To Do
- Decide on final amount of data to keep in each sheet at a time
- Decide on final features/kpis to display in tableau dashboard (e.g. top authors, top entities, top posts, etc.)
- Color / format dashboard 
- Add example bash file to allow scripting for those who don't know how

## Future Features?
I am not sure if I will continue working on this project once the to-do list is done, but here are some possible features I could add to spruce this up should I be so inclined:

1. Change updatePosts to have another attribute e.g. 'whatToPick' which will decide on which features from the reddit object to pick up for addition to the Google Sheet / MySQL database.  I would probably still use the .env file as a stand in for a config file to store all the columns that people may want similar to how it stores the subreddits to browse right now.

2. Instead of getNER I could make it so that the function to apply and the column to apply it to were supplied in the .env file as well.  This is a lower priority than (1) as this basically just automates something that could be added easily, but might be a nice feature for people who don't know how to code.  If this was done, the transformations to be done and the columns on which they should be done would be supplied in the .env file.

3. Change MySQL code to use executemany() to batch insert rows for speed.  Would be very useful for queries that are larger than what I am currently using in my example.

For both (1) and (2) above, I'm unsure how to deal with the requisite tables in the sheets and mysql to be auto-created depending on the supplied inputs.  For now I can just assume that people would build their own column headers (for Google) or table (for MySQL) but maybe I could look into auto-generating the requisite .sql table creation code or automatically adding the Google sheets based on a conditional in the .env file.

(3) seems like a reasonable step to take and I may add this to to-do rather than keeping it in future features soon.
