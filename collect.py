"""
This script is for:
    1. data collection
    2. keyword-based pre-screening

Output files:
    posts_list_raw.csv         → All collected raw posts (unfiltered)
    posts_list_kw_filtered.csv → Posts filtered by keywords
    posts_list_kw_hit_log.json → Keyword hit-rate data by subreddit and time period
"""

import requests
import pandas as pd
import time
import json
import re
from datetime import datetime, timezone


# ─── Global Constants ────────────────────────────────────────────────────────

# to decide if it is in test-mode or not
TEST_MODE = True

# cap on posts per subreddit per time period, depending on mode
PER_PERIOD_LIMIT = 300 if TEST_MODE else 100000

# full list of subreddits — only used when TEST_MODE is False
SUBREDDITS = [
    "mentalhealth",
    "depression",
    "Anxiety",
    "therapy",
    "therapyGPT",
]

# full list of time periods — only used when TEST_MODE is False
TIME_PERIODS = [
    (datetime(2023, 1, 1),  datetime(2023, 1, 31, 23, 59, 59), "202301"),
    (datetime(2023, 2, 1),  datetime(2023, 2, 28, 23, 59, 59), "202302"),
    (datetime(2023, 3, 1),  datetime(2023, 3, 31, 23, 59, 59), "202303"),
    (datetime(2023, 4, 1),  datetime(2023, 4, 30, 23, 59, 59), "202304"),
    (datetime(2023, 5, 1),  datetime(2023, 5, 31, 23, 59, 59), "202305"),
    (datetime(2023, 6, 1),  datetime(2023, 6, 30, 23, 59, 59), "202306"),
    (datetime(2023, 7, 1),  datetime(2023, 7, 31, 23, 59, 59), "202307"),
    (datetime(2023, 8, 1),  datetime(2023, 8, 31, 23, 59, 59), "202308"),
    (datetime(2023, 9, 1),  datetime(2023, 9, 30, 23, 59, 59), "202309"),
    (datetime(2023, 10, 1), datetime(2023, 10, 31, 23, 59, 59), "202310"),
    (datetime(2023, 11, 1), datetime(2023, 11, 30, 23, 59, 59), "202311"),
    (datetime(2023, 12, 1), datetime(2023, 12, 31, 23, 59, 59), "202312"),
    (datetime(2024, 1, 1),  datetime(2024, 1, 31, 23, 59, 59), "202401"),
    (datetime(2024, 2, 1),  datetime(2024, 2, 29, 23, 59, 59), "202402"),
    (datetime(2024, 3, 1),  datetime(2024, 3, 31, 23, 59, 59), "202403"),
    (datetime(2024, 4, 1),  datetime(2024, 4, 30, 23, 59, 59), "202404"),
    (datetime(2024, 5, 1),  datetime(2024, 5, 31, 23, 59, 59), "202405"),
    (datetime(2024, 6, 1),  datetime(2024, 6, 30, 23, 59, 59), "202406"),
    (datetime(2024, 7, 1),  datetime(2024, 7, 31, 23, 59, 59), "202407"),
    (datetime(2024, 8, 1),  datetime(2024, 8, 31, 23, 59, 59), "202408"),
    (datetime(2024, 9, 1),  datetime(2024, 9, 30, 23, 59, 59), "202409"),
    (datetime(2024, 10, 1), datetime(2024, 10, 31, 23, 59, 59), "202410"),
    (datetime(2024, 11, 1), datetime(2024, 11, 30, 23, 59, 59), "202411"),
    (datetime(2024, 12, 1), datetime(2024, 12, 31, 23, 59, 59), "202412"),
    (datetime(2025, 1, 1),  datetime(2025, 1, 31, 23, 59, 59), "202501"),
    (datetime(2025, 2, 1),  datetime(2025, 2, 28, 23, 59, 59), "202502"),
    (datetime(2025, 3, 1),  datetime(2025, 3, 31, 23, 59, 59), "202503"),
    (datetime(2025, 4, 1),  datetime(2025, 4, 30, 23, 59, 59), "202504"),
    (datetime(2025, 5, 1),  datetime(2025, 5, 31, 23, 59, 59), "202505"),
    (datetime(2025, 6, 1),  datetime(2025, 6, 30, 23, 59, 59), "202506"),
    (datetime(2025, 7, 1),  datetime(2025, 7, 31, 23, 59, 59), "202507"),
    (datetime(2025, 8, 1),  datetime(2025, 8, 31, 23, 59, 59), "202508"),
    (datetime(2025, 9, 1),  datetime(2025, 9, 30, 23, 59, 59), "202509"),
    (datetime(2025, 10, 1), datetime(2025, 10, 31, 23, 59, 59), "202510"),
    (datetime(2025, 11, 1), datetime(2025, 11, 30, 23, 59, 59), "202511"),
    (datetime(2025, 12, 1), datetime(2025, 12, 31, 23, 59, 59), "202512"),
    (datetime(2026, 1, 1),  datetime(2026, 1, 31, 23, 59, 59), "202601"),
    (datetime(2026, 2, 1),  datetime(2026, 2, 28, 23, 59, 59), "202602"),
]

# output filenames — defined as constants so renaming only requires changing one line
POSTS_LIST_RAW        = "posts_list_raw.csv"
POSTS_LIST_FILTERED   = "posts_list_kw_filtered.csv"
POSTS_LIST_KW_HIT_LOG = "posts_list_kw_hit_log.json"


# ─── Keyword Lists ────────────────────────────────────────────────────────────

KEYWORDS_PLAIN = [
    "chatgpt",
    "claude",
    "gemini",
    "grok",
    "gpt",
    "copilot",
    "deepseek",
    "ai chatbot",
    "llm",
    "large language model",
    "artificial intelligence",
]

KEYWORDS_REGEX = [
    r"\bai\b",   # matches standalone "ai" only — \b is word boundary, prevents matching "ai" inside words like "email" or "said"
    r"\bai-",    # matches "ai-" prefix e.g. ai-generated, ai-powered — no right boundary so anything after "ai-" is accepted
    # r"..." raw string prefix: prevents Python from interpreting \ before passing to the regex engine
    # without r, \b would be treated as a backspace character by Python, not a word boundary
]


# ─── Keyword Filtering Functions ──────────────────────────────────────────────

def keyword_filter(text):
    # text is full_text (title + body concatenated), not body alone
    text_lower = text.lower()  # convert to lowercase so matching is case-insensitive

    for keyword in KEYWORDS_PLAIN:
        if keyword in text_lower:
            return True  # return immediately once any keyword is found, no need to check the rest

    for pattern in KEYWORDS_REGEX:
        # re.search() scans the text for the pattern — necessary because regex is a rule, not a fixed string
        if re.search(pattern, text_lower):
            return True

    return False  # only reached if no keyword matched — explicitly returns False instead of None


def word_count(text):
    # .split() cuts the text by whitespace into a list of words, len() counts them
    return len(text.split())


# ─── Data Collection Function ─────────────────────────────────────────────────

def fetch_posts_arcticshift(subreddit, after, before, limit=100000):


# ─── Main Workflow ────────────────────────────────────────────────────────────

def main():
    all_raw = []  # blank list to collect all raw posts
    log     = {}  # blank dictionary to store the metadata for each subreddit and time period

    subreddits_to_run = ["Anxiety"] if TEST_MODE else SUBREDDITS
    periods_to_run    = [p for p in TIME_PERIODS if p[2] == "202501"] if TEST_MODE else TIME_PERIODS

    if TEST_MODE:
        print("_" * 50)
        print("Testing mode is on.")
        print(f"Running r/{subreddits_to_run[0]} · {periods_to_run[0][2]}, up to {PER_PERIOD_LIMIT} posts.")
        print("To run the full collection, set TEST_MODE to False.")
        print("_" * 50)

    for sub in subreddits_to_run:  # outer loop: iterates over each subreddit
        log[sub]  = {}
        total_sub = 0

        for (start_dt, end_dt, period_name) in periods_to_run:  # inner loop: iterates over each time period
            start = int(start_dt.timestamp())  # .timestamp() converts datetime to Unix timestamp (seconds since 1970-01-01)
            end   = int(end_dt.timestamp())    # int() required because API only accepts integers, not floats

            print(f"r/{sub} {period_name} is running...")
            posts = fetch_posts_arcticshift(sub, start, end, PER_PERIOD_LIMIT)

            for p in posts:  # innermost loop: iterates over each post returned by fetch_posts_arcticshift
                # each post returned by the API is a dictionary
                # .get(key, default) is a safe way to retrieve a value:
                # if the key exists, return its value
                # if the key does not exist, return the default value instead of crashing
                # or "" is a second layer of protection:
                # if the key exists but the value is None, or "" ensures it becomes ""
                # this is necessary because title and body are later concatenated into full_text
                # None + " " would cause a TypeError, so both must be guaranteed strings
                title     = p.get("title", "") or ""
                body      = p.get("selftext", "") or ""  # Reddit API stores post body under "selftext", not "body"
                full_text = (title + " " + body).strip()  # concatenate title and body, .strip() removes leading/trailing whitespace
                all_raw.append({
                    "post_id":     p.get("id", ""),
                    "subreddit":   sub,
                    "period":      period_name,
                    "title":       title,
                    "body":        body,
                    "full_text":   full_text,
                    "created_utc": p.get("created_utc", 0),
                    "score":       p.get("score", 0),
                    "url":         "https://reddit.com" + p.get("permalink", ""),
                })

            log[sub][period_name] = {"raw_count": len(posts)}  # PEP 8: space after colon in dictionaries
            total_sub += len(posts)
            print(f"     -> has collected {len(posts)} posts\n")

        print(f"-> {total_sub} posts have been collected in r/{sub}\n")

    df_raw = pd.DataFrame(all_raw)  # converts all_raw (a list of dictionaries) into a table: each dictionary becomes a row, keys become column names
    df_raw.to_csv(POSTS_LIST_RAW, index=False, encoding="utf-8-sig")
    # index=False: suppresses the auto-generated row numbers (0, 1, 2...) from being saved as a column
    # encoding="utf-8-sig": BOM-prefixed UTF-8, ensures Chinese characters display correctly when opened in Excel
    # without this, Chinese text would appear as garbled characters in Excel
    # this only affects human readability in Excel — downstream code using pd.read_csv() is unaffected
    print(f"raw collection complete: {len(df_raw)} posts saved to {POSTS_LIST_RAW}\n")

    if df_raw.empty:
        print("no posts have been collected, please check your internet connection or time period settings.")
        return

    # keyword-based pre-filtering
    # .apply(keyword_filter) means: for each row in full_text, call keyword_filter(that row's value)
    # if full_text has 1000 rows, keyword_filter gets called 1000 times, once per row
    df_raw["kw_pass"]    = df_raw["full_text"].apply(keyword_filter)
    df_raw["word_count"] = df_raw["full_text"].apply(word_count)
    df_raw["body_valid"] = df_raw["body"].apply(
        lambda x: x not in ["[deleted]", "[removed]", "", None]
        # lambda x: ... is an anonymous function with no name, used here because the logic is simple and only needed once
        # format: lambda parameter: return_value — the colon separates parameter from what gets returned
        # x not in [...] returns True if x is not in the list, False if it is
    )

    df_filtered = df_raw[
        df_raw["kw_pass"] &
        (df_raw["word_count"] >= 50) &
        df_raw["body_valid"]
    ].copy()  # .copy() creates an independent DataFrame — without it, df_filtered would be a view of df_raw

    df_filtered.to_csv(POSTS_LIST_FILTERED, index=False, encoding="utf-8-sig")

    print("_" * 50)
    print("Keyword filtering hit-rate:")
    print("_" * 50)

    for sub in subreddits_to_run:
        for (_, _, period_name) in periods_to_run:  # _ discards start_dt and end_dt — only period_name is needed here
            raw_n      = log[sub][period_name]["raw_count"]  # read from log — "raw_count" is a hardcoded key, sub and period_name are variables because they change each loop
            filtered_n = len(df_filtered[
                (df_filtered["subreddit"] == sub) &
                (df_filtered["period"] == period_name)
            ])  # boolean indexing: filter df_filtered to rows matching current sub and period, len() counts how many rows remain

            hit_rate = round(filtered_n / raw_n, 3) if raw_n > 0 else 0  # > 0 guards against division by zero

            log[sub][period_name]["kw_filtered_count"] = filtered_n  # writing new keys into existing dict (left side of =)
            log[sub][period_name]["kw_hit_rate"]       = hit_rate

            print(f"  r/{sub} · {period_name}: {raw_n} → {filtered_n} posts ({hit_rate:.1%})")  # :.1% converts float to percentage with 1 decimal place e.g. 0.233 → 23.3%

    with open(POSTS_LIST_KW_HIT_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    # with open(...) as f: standard file-writing pattern — automatically closes the file when done
    # "w": write mode — creates the file if it doesn't exist, overwrites if it does
    # json.dump(): writes the log dictionary to a JSON file
    # ensure_ascii=False: preserves non-ASCII characters (e.g. Chinese) instead of escaping them
    # indent=2: formats the JSON with indentation for human readability

    print(f"\nKeyword hit-rate log saved to {POSTS_LIST_KW_HIT_LOG}")

    if TEST_MODE:
        print("\n Test run complete. Set TEST_MODE to False to begin full collection.")
    else:
        print("\n─── Next Steps ───")
        print("  1. Run screening_prompt.py  → LLM relevance screening")
        print("  2. Run agreement_check.py   → human-LLM agreement validation")
        print("  3. After agreement check passes, proceed to Pilot Coding")


# ─── Entry Point ──────────────────────────────────────────────────────────────

# defensive pattern: prevents main() from being automatically executed when imported
# in Python, importing a file triggers automatic execution of all its top-level code
# when run directly, Python sets __name__ to "__main__" — condition passes, main() runs
# when imported, Python sets __name__ to the filename (e.g. "collect") — condition fails

if __name__ == "__main__":
    main()