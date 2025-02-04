from typing import Dict, List, Tuple
import statistics

class PersonalityAssessment:
    # Define questions for each Big Five trait
    QUESTIONS = {
        "openness": [
            "I enjoy trying new experiences and activities",
            "I am curious about many different things",
            "I enjoy abstract or theoretical discussions",
            "I have a vivid imagination",
            "I appreciate art and creative expression",
            "I prefer variety over routine",
            "I am interested in learning new concepts",
            "I enjoy thinking about complex problems"
        ],
        "conscientiousness": [
            "I am organized and methodical",
            "I pay attention to details",
            "I complete tasks thoroughly",
            "I make plans and follow through",
            "I am punctual and respect deadlines",
            "I think carefully before acting",
            "I keep my belongings neat and tidy",
            "I work hard to achieve my goals"
        ],
        "extraversion": [
            "I enjoy being around people",
            "I start conversations easily",
            "I am comfortable in group situations",
            "I am energized by social interactions",
            "I like being the center of attention",
            "I express myself easily to others",
            "I make friends easily",
            "I prefer active, social environments"
        ],
        "agreeableness": [
            "I am sympathetic to others' feelings",
            "I enjoy helping others",
            "I try to avoid conflicts",
            "I am considerate of others",
            "I cooperate well in group settings",
            "I forgive easily",
            "I trust others easily",
            "I show empathy towards others"
        ],
        "neuroticism": [
            "I worry about things",
            "I get stressed easily",
            "I experience mood swings",
            "I feel anxious in new situations",
            "I am sensitive to criticism",
            "I overthink decisions",
            "I get overwhelmed easily",
            "I tend to be self-critical"
        ]
    }

    @staticmethod
    def get_questions() -> Dict[str, List[str]]:
        """Return all personality assessment questions."""
        return PersonalityAssessment.QUESTIONS

    @staticmethod
    def calculate_trait_score(responses: List[int]) -> Tuple[float, str]:
        """
        Calculate the score for a trait based on responses.
        Returns both numerical score and categorical level.
        """
        avg_score = statistics.mean(responses)
        
        # Determine categorical level
        if avg_score <= 2:
            level = "Low"
        elif avg_score <= 3:
            level = "Moderate-Low"
        elif avg_score <= 4:
            level = "Moderate-High"
        else:
            level = "High"
            
        return avg_score, level

    @staticmethod
    def get_trait_description(trait: str, level: str) -> str:
        """
        Get detailed description based on trait and level.
        """
        descriptions = {
            "openness": {
                "High": "You are very curious, creative, and open to new experiences. You have a strong appreciation for art, emotion, adventure, unusual ideas, and variety of experience.",
                "Moderate-High": "You are generally curious and appreciative of new experiences, while maintaining a balance with familiar situations.",
                "Moderate-Low": "You tend to prefer familiar routines and concrete thinking, while occasionally being open to new experiences.",
                "Low": "You prefer practical, straightforward, and routine experiences. You focus on concrete facts and tradition."
            },
            "conscientiousness": {
                "High": "You are highly organized, responsible, and hardworking. You plan ahead and are detail-oriented in pursuing your goals.",
                "Moderate-High": "You are generally organized and responsible, while maintaining some flexibility in your approach to tasks.",
                "Moderate-Low": "You balance spontaneity with organization, sometimes preferring a more relaxed approach to tasks.",
                "Low": "You prefer a more flexible, spontaneous approach to life. You may find strict schedules and organization limiting."
            },
            "extraversion": {
                "High": "You are very outgoing, energetic, and draw energy from social interactions. You enjoy being around people and seek excitement.",
                "Moderate-High": "You generally enjoy social situations while still appreciating some alone time.",
                "Moderate-Low": "You are somewhat reserved but can be social when necessary. You prefer smaller groups or one-on-one interactions.",
                "Low": "You prefer solitary activities and may find social situations draining. You value your independence and quiet time."
            },
            "agreeableness": {
                "High": "You are very cooperative, compassionate, and considerate of others' feelings. You value harmony and tend to be optimistic about human nature.",
                "Moderate-High": "You are generally cooperative and considerate while maintaining healthy boundaries.",
                "Moderate-Low": "You balance cooperation with self-interest and can be skeptical of others' motives when necessary.",
                "Low": "You tend to be more competitive and skeptical of others' motives. You prioritize your own interests and are comfortable with confrontation."
            },
            "neuroticism": {
                "High": "You tend to experience more stress and anxiety than average. You are sensitive to environmental changes and may worry frequently.",
                "Moderate-High": "You are somewhat sensitive to stress and may experience occasional anxiety or mood fluctuations.",
                "Moderate-Low": "You are generally stable and calm, though you may experience stress in challenging situations.",
                "Low": "You are emotionally stable and resilient to stress. You tend to stay calm under pressure and recover quickly from setbacks."
            }
        }
        return descriptions[trait][level]

    @staticmethod
    def get_work_style_recommendations(personality_traits: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Provide work style recommendations based on personality traits.
        """
        recommendations = {
            "environment_preferences": [],
            "communication_style": [],
            "work_approach": []
        }
        
        # Environment preferences
        if personality_traits["extraversion"] in ["High", "Moderate-High"]:
            recommendations["environment_preferences"].extend([
                "Collaborative workspace",
                "Regular team interactions",
                "Opportunities for networking"
            ])
        else:
            recommendations["environment_preferences"].extend([
                "Quiet workspace",
                "Independent work opportunities",
                "Limited interruptions"
            ])

        # Communication style
        if personality_traits["agreeableness"] in ["High", "Moderate-High"]:
            recommendations["communication_style"].extend([
                "Diplomatic approach",
                "Team-oriented communication",
                "Focus on building consensus"
            ])
        else:
            recommendations["communication_style"].extend([
                "Direct communication",
                "Task-focused interactions",
                "Independent decision-making"
            ])

        # Work approach
        if personality_traits["conscientiousness"] in ["High", "Moderate-High"]:
            recommendations["work_approach"].extend([
                "Structured project management",
                "Detailed planning",
                "Regular progress tracking"
            ])
        else:
            recommendations["work_approach"].extend([
                "Flexible deadlines",
                "Adaptable workflow",
                "Creative problem-solving"
            ])

        return recommendations

    @classmethod
    def assess_personality(cls, responses: Dict[str, List[int]]) -> Dict[str, Dict[str, str]]:
        """
        Assess personality based on questionnaire responses.
        Returns detailed personality profile including trait levels and descriptions.
        """
        profile = {}
        
        for trait, trait_responses in responses.items():
            score, level = cls.calculate_trait_score(trait_responses)
            description = cls.get_trait_description(trait, level)
            
            profile[trait] = {
                "score": score,
                "level": level,
                "description": description
            }
        
        # Add work style recommendations
        trait_levels = {trait: data["level"] for trait, data in profile.items()}
        recommendations = cls.get_work_style_recommendations(trait_levels)
        profile["recommendations"] = recommendations
        
        return profile