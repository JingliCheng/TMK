from typing import Dict, Any
from datetime import datetime

def create_user_record(user_id: str, username: str, features: Dict[str, Any], created_at: datetime = None) -> Dict[str, Any]:
    record = {
        'user_id': user_id,
        'username': username,
        'created_at': created_at or datetime.now(),
        'updated_at': datetime.now(),
        # Demographics
        'age_range': features.get('age_range'),
        'gender': features.get('gender'),
        'location': features.get('location'),
        'income_level': features.get('income_level'),
        'education_level': features.get('education_level'),
        # Health
        'illness_types': str(features.get('illness_types', [])),
        'treatment_history': str(features.get('treatment_history', [])),
        # Interest
        'clinical_trial_interest': features.get('clinical_trial_interest'),
        'money_making_interest': features.get('money_making_interest'),
        # Sentiment
        'clinical_trials_sentiment': features.get('clinical_trials_sentiment'),
        'treatment_sentiment': features.get('treatment_sentiment'),
        # Engagement
        'num_comments': features.get('num_comments', 0),
        'avg_score': features.get('avg_score', 0),
        # New conversation metrics
        'conversation_depth': features.get('max_comment_depth', 0),  # Max depth in comment trees
        'conversation_count': features.get('conversation_count', 0),  # Number of comment threads
        'parent_interactions': features.get('parent_interactions', 0),  # Number of replies to others
        'subreddit_types': features.get('subreddit_types', []),  # Types of subreddits participated in
    }
    return record 