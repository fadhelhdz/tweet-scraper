# Tweet Scraper

A Python-based tool for scraping tweets and storing them in structured formats (JSON and CSV).

## Features

- Scrapes tweets from Twitter
- Stores tweet data including:
  - Tweet text
  - Username
  - Unique user ID
  - Creation timestamp
  - Engagement metrics (retweets, favorites, replies)
  - Media attachments (image paths)
  - Hashtags

## Data Structure

The scraper collects the following information for each tweet:

```json
{
    "tweet_count": 1,
    "unique_id": "user_id",
    "username": "User Name",
    "text": "Tweet content",
    "hashtags": ["hashtag1", "hashtag2"],
    "created_at": "YYYY-MM-DD HH:MM:SS",
    "retweet_count": 0,
    "favorite_count": 0,
    "reply_count": 0,
    "image_paths": ["path/to/image1.jpg"]
}