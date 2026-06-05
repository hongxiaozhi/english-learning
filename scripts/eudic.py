#!/usr/bin/env python3
"""Eudic (欧路词典) API client for managing vocabulary."""

import json
import os
import sys
import requests

CONFIG_PATH = os.path.expanduser("~/.claude/eudic.json")
BASE_URL = "https://api.frdic.com/api/open/v1"


def load_config():
    """Load API token and settings from config file."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Config file not found: {CONFIG_PATH}")
        print("Please create it with your API token.")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_headers(config):
    """Get request headers with authentication."""
    token = config['api_token']
    # Try different token formats
    if token.startswith("NIS "):
        # Token already has prefix
        auth = token
    else:
        auth = f"Bearer {token}"

    return {
        "Authorization": auth,
        "Content-Type": "application/json",
        "User-Agent": "EnglishLearning/1.0"
    }


def get_categories(config):
    """Get all word categories."""
    language = config.get("language", "en")
    url = f"{BASE_URL}/studylist/category?language={language}"
    resp = requests.get(url, headers=get_headers(config))
    resp.raise_for_status()
    return resp.json()


def create_category(config, name):
    """Create a new word category."""
    language = config.get("language", "en")
    url = f"{BASE_URL}/studylist/category"
    data = {"language": language, "name": name}
    resp = requests.post(url, headers=get_headers(config), json=data)
    resp.raise_for_status()
    return resp.json()


def find_category(config, name):
    """Find a category by name, create if not exists."""
    categories = get_categories(config)
    for cat in categories.get("data", []):
        if cat.get("name") == name:
            return cat
    return create_category(config, name)


def add_words(config, words, category_id=None):
    """Add words to a category."""
    language = config.get("language", "en")

    if category_id is None:
        category_name = config.get("default_category", "英语学习")
        cat = find_category(config, category_name)
        category_id = cat.get("id")

    url = f"{BASE_URL}/studylist/words"
    data = {
        "id": category_id,
        "language": language,
        "words": words if isinstance(words, list) else [words]
    }

    resp = requests.post(url, headers=get_headers(config), json=data)
    resp.raise_for_status()
    return resp.json()


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python eudic.py <word1> [word2] [word3] ...")
        print("Example: python eudic.py vocabulary grammar eloquent")
        sys.exit(1)

    config = load_config()
    words = sys.argv[1:]

    print(f"Adding {len(words)} word(s) to Eudic...")
    result = add_words(config, words)

    if result.get("message") and "成功" in result.get("message", ""):
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Error: {result}")

    return result


if __name__ == "__main__":
    main()
