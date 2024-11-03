from typing import List, Dict, Any
import yaml
from pathlib import Path
import os

class Config:
    def __init__(self, config_path: str):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load credentials from environment if not in config
        self._load_credentials()
        # Validate required fields
        self._validate_config()

    def _load_credentials(self):
        """Load credentials from environment variables if not in config"""
        # Reddit credentials
        if not self._get_nested(self.config, ['reddit', 'client_id']):
            self.config['reddit']['client_id'] = os.getenv('REDDIT_CLIENT_ID')
            
        if not self._get_nested(self.config, ['reddit', 'client_secret']):
            self.config['reddit']['client_secret'] = os.getenv('REDDIT_CLIENT_SECRET')
            
        # OpenAI credentials
        if not self._get_nested(self.config, ['openai', 'api_key']):
            self.config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    
        
    def _validate_config(self):
        """Validate required configuration fields"""
        required_fields = [
            ('reddit.client_id', "Reddit client ID is required"),
            ('reddit.client_secret', "Reddit client secret is required"),
            ('openai.api_key', "OpenAI API key is required")
        ]
        
        for field, message in required_fields:
            if not self._get_nested(self.config, field.split('.')):
                raise ValueError(message)
                
    def _get_nested(self, d: Dict, keys: List[str]) -> Any:
        """Get nested dictionary value"""
        for key in keys:
            if not isinstance(d, dict) or key not in d:
                return None
            d = d[key]
        return d
    
    @property
    def reddit_config(self) -> Dict[str, str]:
        return self.config['reddit']
    
    @property
    def subreddits(self) -> List[str]:
        all_subreddits = []
        for category in ['health', 'money']:
            all_subreddits.extend(self.config['subreddits'].get(category, []))
        return all_subreddits
    
    @property
    def directories(self) -> Dict[str, str]:
        return self.config['directories']
    
    @property
    def ranking_config(self) -> Dict[str, Any]:
        return self.config['ranking']
    
    @property
    def scraping_config(self) -> Dict[str, Any]:
        return self.config['scraping'] 