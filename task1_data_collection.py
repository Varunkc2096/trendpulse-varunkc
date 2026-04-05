import requests
import json
import os
import time
from datetime import datetime

HEADERS = {"User-Agent": "TrendPulse/1.0"}

CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "book", "show", "award", "streaming"]
}

MAX_PER_CATEGORY = 40
MIN_PER_CATEGORY = 5

def assign_category(title):
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return None

print("Fetching top story IDs...")
response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", headers=HEADERS)
top_story_ids = response.json()
print("Total story IDs received:", len(top_story_ids))

print("Fetching story details... (this may take a moment)")
fetched_stories = []

for story_id in top_story_ids[:500]:
    try:
        url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(url, headers=HEADERS).json()
        if story and "title" in story:
            fetched_stories.append(story)
    except Exception as e:
        print(f"Skipping story {story_id}: {e}")
        continue

print("Successfully fetched", len(fetched_stories), "stories")

all_stories = []
current_time = datetime.now().isoformat()
category_counts = {cat: 0 for cat in CATEGORIES}

for category in CATEGORIES:
    print("Processing category:", category)
    for story in fetched_stories:
        if category_counts[category] >= MAX_PER_CATEGORY:
            break
        title = story.get("title", "")
        if assign_category(title) == category:
            all_stories.append({
                "post_id":      story.get("id"),
                "title":        title,
                "category":     category,
                "score":        story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author":       story.get("by", "unknown"),
                "collected_at": current_time
            })
            category_counts[category] += 1
    print("  Collected", category_counts[category], "stories for", category)
    time.sleep(2)

os.makedirs("data", exist_ok=True)
today = datetime.now().strftime("%Y%m%d")
filename = f"data/trends_{today}.json"

with open(filename, "w") as f:
    json.dump(all_stories, f, indent=2)

print("Collected", len(all_stories), "stories. Saved to", filename)
