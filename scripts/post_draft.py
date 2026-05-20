#!/usr/bin/env python3
"""リプライをTypefullyにDraftとして保存し、処理済みIDをSupabaseに記録する"""
import os
import json
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

TYPEFULLY_API_KEY = os.environ["TYPEFULLY_API_KEY"]
TYPEFULLY_SOCIAL_SET_ID = os.environ["TYPEFULLY_SOCIAL_SET_ID"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]


def post_to_typefully(reply_text, tweet_url):
    res = requests.post(
        f"https://api.typefully.com/v2/social-sets/{TYPEFULLY_SOCIAL_SET_ID}/drafts",
        headers={
            "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "platforms": {
                "x": {
                    "enabled": True,
                    "posts": [{"text": reply_text}],
                    "settings": {"reply_to_url": tweet_url},
                }
            }
        },
    )
    res.raise_for_status()
    return res.json()


def save_processed(tweet_id):
    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/processed_tweet_ids",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "ignore-duplicates",
        },
        json={"tweet_id": tweet_id},
    )
    res.raise_for_status()


def main():
    if len(sys.argv) < 4:
        print("Usage: post_draft.py <tweet_id> <tweet_url> <reply_text>")
        sys.exit(1)

    tweet_id = sys.argv[1]
    tweet_url = sys.argv[2]
    reply_text = sys.argv[3]

    result = post_to_typefully(reply_text, tweet_url)
    print(f"✓ Draft作成: {result.get('id', 'unknown')}")

    save_processed(tweet_id)
    print(f"✓ Supabaseに記録: {tweet_id}")


if __name__ == "__main__":
    main()
