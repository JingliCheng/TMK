from typing import Dict, Any, List, Tuple
from openai import OpenAI
import json

class FeatureValidator:
    def __init__(self, config: Dict[str, Any]):
        """Initialize with OpenAI configuration"""
        self.openai_config = config['openai']
        self.gpt_client = OpenAI(api_key=self.openai_config['api_key'])
        self.model = self.openai_config.get('model', 'gpt-4o-mini')
        self.temperature = self.openai_config.get('temperature', 0.1)

    def validate_features(self, text: str, features: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate extracted features against original text
        
        Returns:
            Tuple[bool, Dict]: (is_valid, validated_features)
            - is_valid: True if features are mostly valid
            - validated_features: Features with invalid ones removed/corrected
        """
        prompt = f"""
        Analyze if the extracted features are supported by the original text.
        
        Original Text: {text}
        
        Extracted Features:
        {json.dumps(features, indent=2)}
        
        For each feature, analyze if it is valid based on the text.
        
        Return a JSON object in this exact format:
        {{
            "validation_results": {{
                "feature_name": {{
                    "is_valid": boolean,
                    "corrected_value": any or null,
                    "reason": "string explanation"
                }}
            }}
        }}
        
        Example response:
        {{
            "validation_results": {{
                "age": {{
                    "is_valid": false,
                    "corrected_value": null,
                    "reason": "No age information present in text"
                }},
                "sentiment": {{
                    "is_valid": true,
                    "corrected_value": null,
                    "reason": "Clearly negative sentiment expressed in text"
                }}
            }}
        }}
        """

        try:
            response = self.gpt_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a critical validator focused on "
                     "identifying unsupported claims and hallucinations in extracted features."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            validation_results = json.loads(response.choices[0].message.content)
            return self._process_validation(features, validation_results['validation_results'])
            
        except Exception as e:
            print(f"Error in validation: {e}")
            return False, features

    def _process_validation(
        self, 
        original_features: Dict[str, Any], 
        validation_results: Dict[str, Dict]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process validation results and update features accordingly"""
        validated_features = original_features.copy()
        invalid_count = 0
        total_features = len(validation_results)

        for feature_name, result in validation_results.items():
            if feature_name not in original_features:
                continue

            if not result['is_valid']:
                invalid_count += 1
                validated_features[feature_name] = result['corrected_value']

        # Consider validation successful if less than 30% of features are invalid
        is_valid = (invalid_count / total_features) < 0.3 if total_features > 0 else False

        return is_valid, validated_features

    def _process_validation(
        self, 
        original_features: Dict[str, Any], 
        validation_results: Dict[str, Dict]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process validation results and update features accordingly"""
        validated_features = original_features.copy()
        invalid_count = 0
        total_features = len(validation_results)

        for feature_name, result in validation_results.items():
            if feature_name not in original_features:
                continue

            if not result['is_valid']:
                invalid_count += 1
                if result['corrected_value'] is not None:
                    validated_features[feature_name] = result['corrected_value']
                else:
                    validated_features[feature_name] = None

        # Consider validation successful if less than 30% of features are invalid
        is_valid = (invalid_count / total_features) < 0.3 if total_features > 0 else False

        return is_valid, validated_features

    def get_validation_report(self, text: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed validation report"""
        prompt = f"""
        Generate a detailed validation report for the extracted features.
        
        Original Text: {text}
        
        Extracted Features:
        {json.dumps(features, indent=2)}
        
        Analyze:
        1. Overall reliability of extraction
        2. Specific concerns about any features
        3. Suggestions for improvement
        
        Return in JSON format:
        {{
            "reliability_score": float (0-1),
            "feature_analysis": {{
                "feature_name": {{
                    "confidence": float (0-1),
                    "concerns": "string or null",
                    "suggestions": "string or null"
                }}
            }},
            "overall_recommendations": "string"
        }}
        """

        try:
            response = self.gpt_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a detailed feature validation "
                     "analyst providing comprehensive analysis of extraction quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating validation report: {e}")
            return {} 