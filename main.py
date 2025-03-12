from twikit import Client, TooManyRequests
import time
from datetime import datetime, timedelta
import csv
from configparser import ConfigParser
from random import randint
import asyncio
import os

START_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d")
NUM_DAYS = 2
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

        while True:
            try:
                tweets = await get_tweets(client, query, tweets)
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                wait_time = rate_limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue

            if not tweets:
                print(f'{datetime.now()} - No more tweets found')
                break

            for tweet in tweets:
                tweet_count += 1
                tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count, tweet.favorite_count]
                
                with open('tweets.csv', 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(tweet_data)

            print(f'{datetime.now()} - Got {tweet_count} tweets')

        print(f'{datetime.now()} - Done! Got {tweet_count} tweets found')

if __name__ == "__main__":
    asyncio.run(main())