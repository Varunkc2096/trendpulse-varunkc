import requests
import json
import os
import time
from datetime import datetime

# i learned that we need to import libraries before using them
# requests is for getting data from internet
# json is for saving data in json format
# os is for creating folders
# time is for adding delay
# datetime is for getting current date and time

# i read that hackernews needs a header so i added this
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# i made a dictionary with 5 categories and their keywords
# if the title has any of these words it goes to that category
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "book", "show", "award", "streaming"]
}

# i dont want one category to have all stories so i set a max limit
MAX_PER_CATEGORY = 40
# each category should have atleast 5 stories
MIN_PER_CATEGORY = 5

# i made this function to check which category a story belongs to
def assign_category(title):
    # i convert title to lowercase because "AI" and "ai" should both match
    title_lower = title.lower()
    
    # i loop through each category one by one
    for category, keywords in CATEGORIES.items():
        # i check each keyword in that category
        for keyword in keywords:
            # if the keyword is found in title, return that category
            if keyword in title_lower:
                return category
    
    # if no keyword matched, return None (means no category found)
    return None

# first i need to get the list of all top story IDs
# this url gives a list of numbers which are story IDs
response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=HEADERS)

# i convert the response to a python list using .json()
top_story_ids = response.json()

# now i will fetch details of each story using its ID
# i only take 500 because fetching all might take too long
fetched_stories = []  # i created empty list to store stories

for story_id in top_story_ids[:500]:
    try:
        # i put the ID in the url to get that specific story
        url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        
        # i fetch the story and convert it to dictionary
        story = requests.get(url, headers=HEADERS).json()
        
        # some stories are deleted or empty so i skip those
        if story and "title" in story:
            fetched_stories.append(story)  # i add the story to my list

    except Exception as e:
        # if any error happens i just skip that story and move on
        # i dont want my whole code to crash because of one bad story
        continue

# now i will go through each category and collect matching stories
all_stories = []  # this list will have my final stories with all 7 fields

# i save the current time once so all stories have same timestamp
current_time = datetime.now().isoformat()

# i use a dictionary to count how many stories i collected per category
category_counts = {cat: 0 for cat in CATEGORIES}

for category in CATEGORIES:
    # i loop through all stories for each category
    for story in fetched_stories:
        
        # if i already have 40 stories for this category i stop
        if category_counts[category] >= MAX_PER_CATEGORY:
            break
        
        # i get the title of the story
        title = story.get("title", "")
        
        # i check if this story belongs to current category
        if assign_category(title) == category:
            
            # i save all 7 fields that are required
            all_stories.append({
                "post_id":      story.get("id"),             # the unique id of story
                "title":        title,                        # the title of story
                "category":     category,                     # category i assigned
                "score":        story.get("score", 0),        # upvotes, 0 if not found
                "num_comments": story.get("descendants", 0),  # comments, 0 if not found
                "author":       story.get("by", "unknown"),   # who wrote it
                "collected_at": current_time                  # when i collected this
            })
            
            # i increase the count for this category
            category_counts[category] += 1

    # i wait 2 seconds after finishing each category
    # i read that we should not hit the api too fast
    time.sleep(2)

# now i save everything to a json file
# first i create the data folder if it doesnt exist
os.makedirs("data", exist_ok=True)

# i add todays date to the filename so i know when it was created
today = datetime.now().strftime("%Y%m%d")
filename = f"data/trends_{today}.json"

# i open the file and write all stories into it
with open(filename, "w") as f:
    json.dump(all_stories, f, indent=2)  # indent=2 makes it look clean when opened

print(f"\nCollected {len(all_stories)} stories. Saved to {filename}")