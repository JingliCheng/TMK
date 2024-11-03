import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

def init_db() -> pd.DataFrame:
    """Initialize empty users DataFrame"""
    return pd.DataFrame(columns=[
        # User info
        'user_id', 'username', 'created_at', 'updated_at',
        # Demographics
        'age_range', 'gender', 'location', 'income_level', 'education_level',
        # Health
        'illness_types', 'treatment_history',
        # Interest
        'clinical_trial_interest', 'money_making_interest',
        # Sentiment
        'clinical_trials_sentiment', 'treatment_sentiment',
        # Engagement
        'num_comments', 'avg_score',
        # New columns
        'conversation_depth', 'conversation_count',
        'parent_interactions', 'subreddit_types'
    ])

def upsert_user(df: pd.DataFrame, user_data: Dict) -> pd.DataFrame:
    """Insert or update user record"""
    if user_data['user_id'] in df['user_id'].values:
        df.loc[df['user_id'] == user_data['user_id']] = user_data
    else:
        df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
    return df

def query_users(df: pd.DataFrame, criteria: Dict) -> pd.DataFrame:
    """Query users based on criteria
    
    Example criteria:
    {
        'gender': 'M',
        'clinical_trial_interest': 'high',
        'num_comments': ('>', 5)
    }
    """
    mask = pd.Series([True] * len(df))
    
    for column, value in criteria.items():
        if isinstance(value, tuple):
            operator, val = value
            if operator == '>':
                mask &= df[column] > val
            elif operator == '<':
                mask &= df[column] < val
            elif operator == '>=':
                mask &= df[column] >= val
            elif operator == '<=':
                mask &= df[column] <= val
        else:
            mask &= df[column] == value
            
    return df[mask]

def save_db(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame to disk"""
    df.to_pickle(path)

def load_db(path: str) -> pd.DataFrame:
    """Load DataFrame from disk"""
    return pd.read_pickle(path) 