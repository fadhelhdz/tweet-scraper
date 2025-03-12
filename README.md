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
```
## Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/tweet-scraper.git
cd tweet-scraper
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure the scraper
- Create a config.ini file with your Twitter credentials:
```ini
[X]
username=your_username
email=your_email
password=your_password
 ```

## Usage
Run the main script:

```bash
python main.py
 ```

## Output
The scraper generates output file:

- tweets.json : Contains the full tweet data in JSON format

## Requirements
- Python 3.x
- twikit: Twitter scraping library
- See requirements.txt for additional Python package dependencies
## Acknowledgments
This project is built using twikit , an excellent Twitter scraping library that handles authentication, rate limiting, and data collection. Special thanks to the twikit developers for making this tool possible.