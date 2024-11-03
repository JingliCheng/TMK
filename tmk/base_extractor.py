from typing import Dict, Any
from openai import OpenAI
import json

class BaseFeatureExtractor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize with OpenAI configuration"""
        self.openai_config = config['openai']
        self.gpt_client = OpenAI(api_key=self.openai_config['api_key'])
        self.model = self.openai_config.get('model', 'gpt-4o-mini')
        self.temperature = self.openai_config.get('temperature', 0.1)
        
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract all features from text in a single GPT call"""
        output_format = {
            # Demographics
            "age_range": "string or null",
            "gender": "string or null",
            "location": "string or null",
            "income_level": "string or null",  # high/medium/low
            "education_level": "string or null",  # high/medium/low
            # Health
            "illness_types": ["string"],  # list of illnesses
            "treatment_history": ["string"],  # list of treatments
            # Interest
            "clinical_trial_interest": "string or null",  # high/medium/low
            "money_making_interest": "string or null",  # high/medium/low
            # Sentiment
            "clinical_trials_sentiment": "float or null",  # -1 to 1
            "treatment_sentiment": "float or null"  # -1 to 1
        }

        prompt = f"""
        Analyze the following text and extract user information. Only extract information that is explicitly mentioned or can be confidently inferred.
        If uncertain about any field, return null.

        Text: {text}

        Extract:
        1. Demographics:
           - Age range (e.g., "18-24", "25-34", etc.)
           - Gender (M/F/Other)
           - Location (city, state, or country)
           - Income level (high/medium/low) based on mentioned job, lifestyle
           - Education level (high/medium/low) based on vocabulary, mentioned background

        2. Health Information:
           - List any mentioned illnesses or conditions
           - List any mentioned treatments or medications

        3. Interest in Clinical Trials:
           - Rate interest in clinical trials (high/medium/low)
           - Rate interest in making money from trials (high/medium/low)

        4. Sentiment Analysis:
           - Score sentiment towards clinical trials (-1 to 1)
           - Score sentiment towards current/past treatments (-1 to 1)

        Reason step by step, but only include the final values in your JSON response.
        """

        try:
            response = self.gpt_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise feature extractor. "
                     "Extract only the information that is explicitly mentioned or can be "
                     "confidently inferred from the text. If uncertain, return null."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._clean_extraction(result)
            
        except Exception as e:
            print(f"Error in GPT API call: {e}")
            return {}

    def _clean_extraction(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize extracted features"""
        cleaned = {}
        for key, value in extraction.items():
            # Convert empty strings or "null"/"none" strings to None
            if value == "" or (isinstance(value, str) and value.lower() in ["null", "none"]):
                cleaned[key] = None
            # Convert string representations of lists to actual lists
            elif key in ["illness_types", "treatment_history"] and isinstance(value, str):
                cleaned[key] = eval(value) if value.startswith("[") else [value]
            # Keep other values as is
            else:
                cleaned[key] = value
        return cleaned