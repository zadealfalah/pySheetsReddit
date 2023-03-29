# pySheetsReddit
Automating Tableau output with Python and Google Sheets / Drive

## Table of Contents
* [General Info](#general-info)
* [Current Features](#curent-features)
* [To Do](#to-do)

## General Info
This project seeks to automatically generate and update a public Tableau dashboard with data pulled from Reddit.

## Current Features
Currently, the data is taken from Reddit using PRAW and pushed into Google Sheets.  The data includes the time a post was created, the subreddit it was created on, as well as the title, self text, author, score, and ID of the post.  The subreddits that these are taken from can be set manually along with the total number of 'top' posts from each subreddit to take.  By default, it takes the top 100 posts within the last week from the 'test' subreddit.  This is all done in the **updatePosts()** function.

Another function called **getNER()** takes the data from **updatePosts()** and performs NER with spaCy on the titles and self texts of the posts then adds this information to different Google worksheet.  

Finally, a function called **cleanSheetByTime()** cleans a given worksheet by batch removing all rows that are outside of our area of interest - namely the last week.

## To Do
- Upload public tableau dashboard created from these worksheets
- Decide on final amount of data to keep in each sheet at a time
- Decide on final features to display in tableau dashboard (e.g. top authors, top entities, top posts, etc.)
- Schedule cron job to update automatically
- Could also switch to MySQL and get a much larger dataset (more subreddits, longer timeframe, more posts, etc.)
