from typing import List, Dict, Any
import json
import os
import glob
import pandas as pd
from datetime import datetime
from tmk.base_extractor import BaseFeatureExtractor
from tmk.validation import FeatureValidator
from tmk.user import create_user_record
from tmk.database import init_db, upsert_user, save_db

def _process_comment_tree(comment_data, user_contents):
    """Process hierarchical comment data"""
    # Skip deleted/removed comments or those without authors
    if not comment_data.get('author') or comment_data['author'] in ['[deleted]', '[removed]']:
        return
        
    # Add comment to user's content
    if comment_data['author'] not in user_contents:
        user_contents[comment_data['author']] = []
    
    user_contents[comment_data['author']].append({
        'content': comment_data.get('text', ''),
        'score': comment_data.get('score', 0),
        'depth': comment_data.get('depth', 0),
        'parent_id': comment_data.get('parent_id'),
        'subreddit': comment_data.get('subreddit'),
        'subreddit_type': comment_data.get('subreddit_type')
    })
    
    # Process replies recursively
    for reply in comment_data.get('replies', []):
        _process_comment_tree(reply, user_contents)

def process_raw_data(
    raw_data_dir: str = "raw_data",
    processed_dir: str = "processed_data",
    db_path: str = "data/users.pkl",
    config = None,
) -> None:
    """Process raw data files and update database"""
    extractor = BaseFeatureExtractor(config.config)
    validator = FeatureValidator(config.config)
    
    # Initialize or load database
    if os.path.exists(db_path):
        users_df = pd.read_pickle(db_path)
    else:
        users_df = init_db()

    # Create processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)

    # Get all unprocessed JSON files
    raw_files = glob.glob(f"{raw_data_dir}/*.json")
    processed_files = set(os.path.basename(f).replace('.json', '.processed')
                         for f in glob.glob(f"{processed_dir}/*.processed"))
    
    for raw_file in raw_files:
        filename = os.path.basename(raw_file)
        if filename.replace('.json', '.processed') in processed_files:
            print(f"Skipping already processed file: {filename}")
            continue

        print(f"Processing {filename}...")
        
        # Load raw data
        with open(raw_file, 'r') as f:
            raw_data = json.load(f)

        # Process each user's content
        user_contents = {}
        for post in raw_data:
            # Process post
            if post.get('author'):
                if post['author'] not in user_contents:
                    user_contents[post['author']] = []
                user_contents[post['author']].append({
                    'content': f"Title: {post['title']}\n{post['text']}",
                    'score': post['score'],
                    'subreddit': post['subreddit'],
                    'subreddit_type': post['subreddit_type']
                })
            
            # Process comment tree
            for comment in post.get('comments', []):
                _process_comment_tree(comment, user_contents)

        # Process each user
        for username, contents in user_contents.items():
            # Combine all user's content
            combined_text = "\n---\n".join(
                f"[r/{c['subreddit']}] {c['content']}" for c in contents
            )
            
            # Extract features
            features = extractor.extract_features(combined_text)
            
            # Validate features
            is_valid, validated_features = validator.validate_features(
                combined_text, features
            )
            
            if not is_valid:
                print(f"Warning: Potential hallucinations in features for user {username}")
            
            # Add engagement metrics
            validated_features['num_comments'] = len(contents)
            validated_features['avg_score'] = sum(c['score'] for c in contents) / len(contents)
            
            # Create and upsert user record
            user_record = create_user_record(
                user_id=username,
                username=username,
                features=validated_features
            )
            users_df = upsert_user(users_df, user_record)

        # Mark file as processed
        processed_mark = f"{processed_dir}/{filename.replace('.json', '.processed')}"
        with open(processed_mark, 'w') as f:
            f.write(str(datetime.now()))

    # Save updated database
    save_db(users_df, db_path)
    print(f"Database updated at {db_path}") 