from typing import Dict, List
import pandas as pd
import numpy as np
from tmk.set_config import Config

class UserRanker:
    def __init__(self, config: Config):
        """Initialize with config"""
        self.config = config
        self.ranking_criteria = {}  # Will be set in rank_users_by_type
        
    def calculate_ranking_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate ranking scores for all users"""
        # Initialize scores with zeros
        scores = np.zeros(len(df))
        
        for column, weight in self.ranking_criteria.items():
            if column in df.columns:
                # Convert to numeric, replacing non-numeric with NaN
                values = pd.to_numeric(df[column], errors='coerce')
                
                # Skip if all values are NaN
                if values.isna().all():
                    continue
                    
                # Normalize non-NaN values to 0-1 range
                min_val = values.min()
                max_val = values.max()
                if max_val > min_val:
                    normalized = (values - min_val) / (max_val - min_val)
                    scores += normalized.fillna(0) * weight
        
        # Add scores to DataFrame
        df_with_scores = df.copy()
        df_with_scores['ranking_score'] = scores.astype(float)
        return df_with_scores

    def rank_users_by_type(self, df: pd.DataFrame, user_type: str) -> pd.DataFrame:
        """Rank users based on predefined user types"""
        # Get criteria from config
        if user_type == "money_motivated":
            self.ranking_criteria = self.config.ranking_config['money_motivated_weights']
        elif user_type == "treatment_seeking":
            self.ranking_criteria = self.config.ranking_config['treatment_seeking_weights']
        else:
            raise ValueError(f"Unknown user type: {user_type}")
            
        return self.calculate_ranking_scores(df)