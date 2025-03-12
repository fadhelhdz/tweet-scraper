from twikit import Client, TooManyRequests
import time
from datetime import datetime, timedelta
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import os
import httpx

START_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d")
NUM_DAYS = 2
folder_path = os.path.join(os.getcwd(), "images")
json_file = 'tweets.json'
cookies_file = 'cookies.json'

async def get_tweets(client, query, tweets):
    if tweets is None:
        #* get tweets
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(query, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        time.sleep(wait_time)
        tweets = await tweets.next()
    return tweets

async def login_or_load_cookies(client, username, email, password):
    """Check if cookies exist; if not, log in and save them."""
    if os.path.exists(cookies_file):
        print(f"{datetime.now()} - Loading cookies from {cookies_file}")
        client.load_cookies(cookies_file)
    else:
        print(f"{datetime.now()} - Cookies not found. Logging in...")
        await client.login(auth_info_1=username, auth_info_2=email, password=password)
        client.save_cookies(cookies_file)
        print(f"{datetime.now()} - Cookies saved to {cookies_file}")

async def save_tweets_to_json(tweets_list):
    """Save the updated tweets list back to the JSON file."""
    async with aiofiles.open(json_file, mode='w', encoding='utf-8') as file:
        await file.write(json.dumps(tweets_list, ensure_ascii=False, indent=4))

async def load_existing_tweets():
    """Load existing tweets if the JSON file exists; else return an empty list."""
    if os.path.exists(json_file):
        async with aiofiles.open(json_file, mode='r', encoding='utf-8') as file:
            content = await file.read()
            return json.loads(content) if content.strip() else []
    return []

async def download_media_with_retry(media, file_path, image_paths, retries=3):
    """Download media with retries. On failure, append 'failed to download' and continue."""
    for attempt in range(1, retries + 1):
        try:
            print(f"Download Attempt {attempt}: Downloading {media.media_url}")
            await media.download(file_path)  # Keep existing media.download
            image_paths.append(file_path)     # Append path on success
            print(f"Downloaded to {file_path}")
            return True  # Successful download
        except httpx.ConnectTimeout:
            print(f"Timeout: Attempt {attempt}/{retries} failed.")
            if attempt < retries:
                await asyncio.sleep(5)  # Wait before retrying
        except Exception as e:
            print(f"Error: {e}")
            break

    # After all retries fail
    print(f"Failed after {retries} retries for {media.media_url}")
    image_paths.append("failed to download")  # Record failure
    return False  #Indicate failure

async def main():
    # Load credentials
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    # # Login 
    # await client.login(auth_info_1=username, auth_info_2=email, password=password)
    # client.save_cookies('cookies.json')

    # Initialize client
    client = Client(language='en-US')
    await login_or_load_cookies(client, username, email, password)

    tweet_count = 0

    for day_offset in range(NUM_DAYS):
        since_date = (START_DATE + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        until_date = (START_DATE + timedelta(days=day_offset + 1)).strftime('%Y-%m-%d')
        query = f'100 hari "Prabowo" since:{since_date} until:{until_date}'
        
        tweets = None
        daily_tweets = []

        while True:
            try:
                tweets = await get_tweets(client, query, tweets)
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                wait_time = (rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
                continue

            if not tweets:
                if daily_tweets:
                    all_tweets.extend(daily_tweets)
                    await save_tweets_to_json(all_tweets)
                    print(f'{datetime.now()} - Saved {len(daily_tweets)} tweets for {since_date}. Total: {len(all_tweets)}')
                print(f'{datetime.now()} - No more tweets found for {since_date}. Moving to next day.')
                break

            for tweet in tweets:
                if tweet.lang in ['in', 'en']:
                    tweet_count += 1
                    image_paths = []

                    # Download and save images
                    if hasattr(tweet, 'media') and tweet.media:
                        for i, media in enumerate(tweet.media):
                            file_path = os.path.join(folder_path, f'media_{tweet_count}_{i}.jpg')
                            success = await download_media_with_retry(media, file_path, image_paths)
                            if not success:
                                print(f"⚠️ Skipping media for tweet {tweet_count} due to failed downloads.")
                                break  # 🚀 Move to the next tweet after failure

                    tweet_data = {
                        "tweet_count": tweet_count,
                        "unique_id": tweet.user.screen_name,
                        "username": tweet.user.name,
                        "text": tweet.full_text or tweet.text,
                        "hashtags": tweet.hashtags if tweet.hashtags else [],
                        "created_at": tweet.created_at_datetime.strftime('%Y-%m-%d %H:%M:%S') if tweet.created_at_datetime else None,
                        "retweet_count": tweet.retweet_count or 0,
                        "favorite_count": tweet.favorite_count or 0,
                        "reply_count": tweet.reply_count or 0,
                        "image_paths": image_paths
                    }

                    daily_tweets.append(tweet_data)
                else:
                    continue

            print(f'{datetime.now()} - Collected {len(daily_tweets)} tweets for {since_date}.')

    print(f'{datetime.now()} - Done! Total tweets collected: {tweet_count}')

if __name__ == "__main__":
    asyncio.run(main())