#!/usr/bin/env python3
"""監視アカウントの未処理ツイートを取得してJSON出力する"""
import os
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

TWITTER_API_KEY = os.environ["TWITTERAPI_IO_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ACCOUNTS_FILE = BASE_DIR / "accounts.json"
TWEETS_PER_ACCOUNT = 3


def load_processed():
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/processed_tweet_ids?select=tweet_id",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    res.raise_for_status()
    return {row["tweet_id"] for row in res.json()}


def get_latest_tweets(username):
    res = requests.get(
        "https://api.twitterapi.io/twitter/user/last_tweets",
        headers={"X-API-Key": TWITTER_API_KEY},
        params={"userName": username},
    )
    res.raise_for_status()
    return res.json().get("data", {}).get("tweets", [])[:TWEETS_PER_ACCOUNT]


def main():
    with open(ACCOUNTS_FILE) as f:
        accounts = json.load(f)

    processed = load_processed()
    results = []

    for username in accounts:
        try:
            tweets = get_latest_tweets(username)
            for tweet in tweets:
                if tweet["id"] in processed:
                    continue
                if tweet["text"].startswith("RT @"):
                    continue
                created_at = datetime.strptime(tweet["createdAt"], "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) - created_at > timedelta(hours=12):
                    continue
                results.append({
                    "id": tweet["id"],
                    "username": username,
                    "text": tweet["text"],
                    "url": tweet["url"],
                })
        except Exception as e:
            import sys
            print(f"Error @{username}: {e}", file=sys.stderr)
        time.sleep(5)

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
