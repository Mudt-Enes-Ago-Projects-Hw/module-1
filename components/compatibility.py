from typing import Tuple, Dict
from .worker import Worker

class CompatibilityCalculator:
    @staticmethod
    def compute_compatibility(user_a: Worker, user_b: Worker) -> Tuple[int, Dict]:
        """Compute compatibility score between two workers"""
        hobby_matches = len(set(user_a.hobbies) & set(user_b.hobbies))
        lang_matches = len(set(user_a.languages) & set(user_b.languages))
        age_diff = abs(user_a.age - user_b.age)

        # Calculate percentage-based scores
        # If user_a has hobbies, calculate what percentage of their hobbies match
        if user_a.hobbies:
            hobby_percentage = (hobby_matches / len(user_a.hobbies)) * 100
            hobby_points = (hobby_percentage / 100) * 30  # Max 30 points for hobbies
        else:
            hobby_percentage = 0
            hobby_points = 0
        
        # Same for languages
        if user_a.languages:
            lang_percentage = (lang_matches / len(user_a.languages)) * 100
            lang_points = (lang_percentage / 100) * 30  # Max 30 points for languages
        else:
            lang_percentage = 0
            lang_points = 0
        
        # Age points (max 40 points)
        if age_diff <= 2:
            age_points = 40
        elif age_diff <= 5:
            age_points = 25
        elif age_diff <= 10:
            age_points = 10
        else:
            age_points = 0

        raw_score = hobby_points + lang_points + age_points
        final_score = min(100, round(raw_score))

        breakdown = {
            'hobby_matches': hobby_matches,
            'hobby_percentage': round(hobby_percentage, 1) if user_a.hobbies else 0,
            'hobby_points': round(hobby_points, 1),
            'lang_matches': lang_matches,
            'lang_percentage': round(lang_percentage, 1) if user_a.languages else 0,
            'lang_points': round(lang_points, 1),
            'age_diff': age_diff,
            'age_points': age_points,
            'final_score': final_score,
            'matching_hobbies': list(set(user_a.hobbies) & set(user_b.hobbies)),
            'matching_languages': list(set(user_a.languages) & set(user_b.languages))
        }

        return final_score, breakdown