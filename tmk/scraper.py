from typing import List, Dict, Any
import praw
from datetime import datetime
import json
import os

class RedditScraper:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize Reddit API client"""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def get_comment_tree(self, comment, depth=0, max_depth=3):
        """Recursively get comment tree"""
        if not comment.author:
            return None
            
        comment_data = {
            'type': 'comment',
            'id': comment.id,
            'author': comment.author.name,
            'text': comment.body,
            'score': comment.score,
            'depth': depth,
            'created_utc': comment.created_utc,
            'parent_id': comment.parent_id,  # Track parent relationship
            'replies': []
        }
        
        if depth < max_depth:
            comment.replies.replace_more(limit=0)
            for reply in comment.replies:
                reply_data = self.get_comment_tree(reply, depth + 1, max_depth)
                if reply_data:
                    comment_data['replies'].append(reply_data)
        
        return comment_data

    def scrape_subreddit(
        self, 
        subreddit_name: str, 
        post_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Updated scrape_subreddit to include comment hierarchies"""
        subreddit = self.reddit.subreddit(subreddit_name)
        raw_data = []

        for submission in subreddit.hot(limit=post_limit):
            # Get post data
            post_data = {
                'type': 'post',
                'id': submission.id,
                'author': submission.author.name if submission.author else None,
                'title': submission.title,
                'text': submission.selftext,
                'score': submission.score,
                'created_utc': submission.created_utc,
                'subreddit': subreddit_name,
                'subreddit_type': 'clinical_trials' if subreddit_name in ['clinical_trials', 'passive_income'] else 'health',
                'comments': []  # Store hierarchical comments
            }
            
            submission.comments.replace_more(limit=0)
            for comment in submission.comments:
                comment_tree = self.get_comment_tree(comment)
                if comment_tree:
                    post_data['comments'].append(comment_tree)
            
            raw_data.append(post_data)

        return raw_data

def scrape_health_subreddits(
    client_id: str, 
    client_secret: str, 
    user_agent: str,
    output_dir: str = "raw_data",
    subreddits: List[str] = None
) -> None:
    """Main function to scrape health-related subreddits and save raw data"""
    if subreddits is None:
        subreddits = [
            "ChronicPain",
            "Fibromyalgia",
            "chronicillness",
            "clinical_trials",
            "passive_income"
        ]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    scraper = RedditScraper(client_id, client_secret, user_agent)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for subreddit in subreddits:
        print(f"Scraping r/{subreddit}...")
        raw_data = scraper.scrape_subreddit(subreddit)
        
        # Save raw data to JSON file
        filename = f"{output_dir}/{subreddit}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(raw_data, f, indent=2)
        print(f"Saved {len(raw_data)} items to {filename}") 