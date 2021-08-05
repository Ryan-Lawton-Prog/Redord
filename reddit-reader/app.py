
from config import MongoDataBase
import praw
import json
import os
from urllib.request import urlretrieve

DB = MongoDataBase()

with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as f:
  data = json.load(f)

reddit = praw.Reddit(
    user_agent=data['user_agent'],
    client_id=data['client_id'],
    client_secret=data['client_secret'],
    username=data['username'],
    password=data['password']
)

print(reddit.user.me())

extension_list = [
    'png',
    'jpg',
    'jpeg',
    'gif'
]

"""
API ENDPOINTS
"""
def check_subs():
    sub_string = ""
    subreddits = DB.get_collection("subreds")
    number_of_subreddits = subreddits.count()
    for subreddit in subreddits.find():
        if len(sub_string) > 0:
            sub_string += '+'+subreddit['name']
        else:
            sub_string = subreddit['name'] 

    subreddit = reddit.subreddit(sub_string)
    for submission in subreddit.stream.submissions():
        subreddits = DB.get_collection("subreds")
        if number_of_subreddits < subreddits.count():
            break
        
        sub_posts = DB.get_collection(submission.subreddit.display_name.lower())
        post = {}
        post['title'] = submission.title
        post['18+'] = submission.over_18
        post['url'] = submission.url
        post['permalink'] = submission.permalink
        post['used'] = False

        if submission.url.split('.')[-1] in extension_list and submission.subreddit.display_name.lower() in data['subs']:
            save_location = "%s%s" % (data['save_dir'],submission.url.split('/')[-1])
            print(save_location)
            print(submission.url, save_location)
            urlretrieve(submission.url, save_location)

        if not (sub_posts.find({'title': submission.title, 'url': submission.url}).count() > 0):
            print(submission, submission.subreddit.display_name, submission.title)
            sub_posts.insert_one(post)

while True:
    check_subs()