import requests
import json
import os
import time
from datetime import datetime

# these libraries help us fetch data from internet, save files, and work with time

# --- Configuration ---
# this header tells the API who we are
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# these are the 5 categories and their keywords
# if a story title contains any of these words, it belongs to that category
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "book", "show", "award", "streaming"]
}

# i set max to 40 so one category doesn't take all the stories
MAX_PER_CATEGORY = 40
# minimum 5 stories per category
MIN_PER_CATEGORY = 5

# this function checks which category a story belongs to
# it converts the title to lowercase so matching works for both "AI" and "ai"
def assign_category(title):
    title_lower = title.lower()  # convert to lowercase for case-insensitive matching
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category  # return the first category that matches
    return None  # if no keyword matched, return nothing

# Step 1: get the list of top story IDs from HackerNews
# this gives us a list of numbers (IDs), not the actual stories yet
response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=HEADERS)
top_story_ids = response.json()  # convert response to python list

# Step 2: use each ID to fetch the actual story details
# we only take first 500 IDs to avoid fetching too many
fetched_stories = []  # empty list to store all stories we fetch

for story_id in top_story_ids[:500]:
    try:
        # build the url for each story using its ID
        url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(url, headers=HEADERS).json()  # fetch and convert to dictionary

        # some stories might be empty or deleted, so we skip those
        if story and "title" in story:
            fetched_stories.append(story)  # add valid story to our list

    except Exception as e:
        # if something goes wrong with one story, skip it and continue
        continue

# Step 3: go through each category and pick matching stories
all_stories = []  # this will hold our final list of stories with all 7 fields
current_time = datetime.now().isoformat()  # save current time once for all stories
category_counts = {cat: 0 for cat in CATEGORIES}  # keep count of stories per category

for category in CATEGORIES:
    # loop through all fetched stories for each category
    for story in fetched_stories:

        # stop collecting for this category once we hit the max limit
        if category_counts[category] >= MAX_PER_CATEGORY:
            break

        title = story.get("title", "")  # get the title, use empty string if missing

        # check if this story matches the current category
        if assign_category(title) == category:

            # extract all 7 required fields and save them
            all_stories.append({
                "post_id":      story.get("id"),             # unique ID of the story
                "title":        title,                        # story title
                "category":     category,                     # category we assigned
                "score":        story.get("score", 0),        # number of upvotes (0 if missing)
                "num_comments": story.get("descendants", 0),  # number of comments (0 if missing)
                "author":       story.get("by", "unknown"),   # author username
                "collected_at": current_time                  # when we collected this data
            })
            category_counts[category] += 1  # increase count for this category

    # wait 2 seconds after each category as required by the task
    time.sleep(2)

# Step 4: save everything to a json file inside data/ folder
os.makedirs("data", exist_ok=True)  # create data/ folder if it doesn't exist

# filename includes today's date so it's easy to identify
today = datetime.now().strftime("%Y%m%d")
filename = f"data/trends_{today}.json"

# write the list of stories into the json file
with open(filename, "w") as f:
    json.dump(all_stories, f, indent=2)  # indent=2 makes the file easier to read

print(f"\nCollected {len(all_stories)} stories. Saved to {filename}")