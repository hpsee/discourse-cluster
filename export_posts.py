#!/usr/bin/env python

from datetime import datetime
import json
import os
from time import sleep
import sys
import re
import requests

# The user must provide a data folder to export to
if len(sys.argv) < 2:
    sys.exit("Please specify the folder to write post exports to.")

export_folder = os.path.abspath(sys.argv[1])
if not os.path.exists(export_folder):
    sys.exit("%s does not exist, create and run again." % export_folder)

# Sleep time in seconds (to not go above api limit)
sleep_time = 1.5
api_key = os.environ.get('DISCOURSE_API_KEY')
username = os.environ.get('DISCOURSE_API_USER')
api_base = os.environ.get('DISCOURSE_BASE', 'https://ask.cyberinfrastructure.org')
category = os.environ.get('DISCOURSE_CATEGORY', 'q-a')

if not api_key or not username:
    sys.exit("Please export your DISCOURSE_API_KEY and DISOURCE_API_USER")

print("Category is %s" % category)
url = "%s/c/%s.json" %(api_base, category)

headers = {
    "Api-Key": api_key,
    "Api-Username": username
}

topics = []
tags = [] # top tags

while url is not None:

    print("Getting %s" % url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:

        # users, primary_groups, topic_list
        results = response.json().get('topic_list', {})
        topics = topics + results.get('topics', [])
        tags = tags + results.get('top_tags', [])

        # /c/q-a?page=1
        url = results.get('more_topics_url', None)

        if url is not None:

            # We have to add the json
            url, params = url.split('?', 1)
            url = "%s%s.json?%s" %(api_base, url, params)

print("Found %s topics, and %s top tags!" %(len(topics), len(tags)))

# Create a folder within data organized by date
now = datetime.now()
date_folder = "%s-%s-%s" %(now.year, now.month, now.day)
export_folder = os.path.join(export_folder, date_folder)
if not os.path.exists(export_folder):
    os.mkdir(export_folder)
    
prefix = re.sub('(http://|https://)', '', api_base) + "-%s" % category
prefix = prefix + '-%s-' + date_folder + ".json" 
export_path = os.path.join(export_folder, prefix)

def write_json(json_object, output_file, mode='w'):
    '''pretty print a json object to file'''
    with open(output_file, mode) as filey:
        filey.writelines(json.dumps(json_object, indent=4))

# Save to file, with date and board
write_json(topics, export_path % "topics")
write_json(tags, export_path % "tags")

# Keep a lookup of all post text by id
posts = {}

# Now we want to get the posts for each topic!
for topic in topics:
    
    # First we need to get all post ids for a topic
    url = "%s/t/%s/%s.json" %(api_base, topic['slug'], topic['id'])

    print("Exporting post %s" % url)
    response = requests.get(url, headers=headers, data={'print': True})
    if response.status_code == 200:
        post = response.json()
        content = [x['cooked'] for x in post['post_stream']['posts']]
        posts[post['id']] = content
        post_id = "post-%s" % post['id']
        write_json(post, export_path % post_id)
        sleep(sleep_time)
    else:
        print("Issue with %s" % url)

# Save post text content to file
write_json(posts, export_path % "posts")
