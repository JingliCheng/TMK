import os
from typing import Dict
import json
from datetime import datetime
from tmk.set_config import Config
from tmk.scraper import RedditScraper
from tmk.user_ranker import UserRanker
from tmk.database import load_db

def setup_directories(config: Config) -> None:
    """Create necessary directories if they don't exist"""
    for dir_path in config.directories.values():
        os.makedirs(dir_path, exist_ok=True)

def scrape_subreddits(config: Config) -> None:
    """Scrape data from specified subreddits"""
    scraper = RedditScraper(**config.reddit_config)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for subreddit in config.subreddits:
        print(f"\nScraping r/{subreddit}...")
        raw_data = scraper.scrape_subreddit(
            subreddit, 
            post_limit=config.scraping_config['post_limit']
        )
        
        # Save raw data
        filename = f"{config.directories['raw_data']}/{subreddit}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(raw_data, f, indent=2)
        print(f"Saved {len(raw_data)} posts to {filename}")

def rank_and_report(config: Config) -> None:
    """Generate ranking reports for different user types"""
    db_path = f"{config.directories['data']}/users.pkl"
    df = load_db(db_path)
    
    ranker = UserRanker(config)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for user_type in ["money_motivated", "treatment_seeking"]:
        print(f"\nGenerating report for {user_type} users...")
        ranked_df = ranker.rank_users_by_type(df, user_type)
        top_users = ranked_df.nlargest(config.ranking_config['top_n'], 'ranking_score')
        
        report_path = f"{config.directories['data']}/{user_type}_report_{timestamp}.csv"
        top_users.to_csv(report_path, index=False)
        print(f"Saved top {config.ranking_config['top_n']} {user_type} users to {report_path}") 