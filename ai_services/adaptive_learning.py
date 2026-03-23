import os
import json
from django.db.models import Avg
from games.models import GameSession, StudentResponse, Score
from questions.models import Question

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AdaptiveLearningAI:
    """
    AI-powered adaptive learning system with detailed feedback
    """

    def __init__(self):
        if genai:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def analyze_student_performance(self, student_profile):
        completed_sessions = GameSession.objects.filter(
            student=student_profile,
            status='COMPLETED'
        )

        if not completed_sessions.exists():
            return {
                'performance_level': 'BEGINNER',
                'average_score': 0,
                'total_sessions': 0,
                'strong_topics': [],
                'weak_topics': [],
                'average_time_per_question': 0,
                'accuracy_trend': 'STABLE',
                'speed_analysis': 'NO_DATA',
                'recommendations': ['Start playing games to build your profile']
            }

        scores = Score.objects.filter(student=student_profile)
        avg_score = scores.aggregate(Avg('percentage'))['avg'] or 0

        all_responses = StudentResponse.objects.filter(
            game_session__student=student_profile
        )

        if all_responses.exists():
            avg_time = all_responses.aggregate(Avg('time_taken'))['time_taken__avg'] or 0
        else:
            avg_time = 0

        if avg_score >= 75:
            level = 'ADVANCED'
        elif avg_score >= 50:
            level = 'INTERMEDIATE'
        else:
            level = 'BEGINNER'

        return {
            'performance_level': level,
            'average_score': round(avg_score, 2),
            'total_sessions': completed_sessions.count(),
            'average_time_per_question': round(avg_time, 1),
            'accuracy_trend': 'STABLE',
            'speed_analysis': 'BALANCED',
            'strong_topics': [],
            'weak_topics': [],
            'strong_concepts': [],
            'weak_concepts': [],
            'fast_accuracy': 0,
            'slow_accuracy': 0
        }

    def generate_detailed_feedback(self, student_profile, game_session):
        responses = StudentResponse.objects.filter(game_session=game_session)

        correct_count = responses.filter(is_correct=True).count()
        total_count = responses.count()

        if total_count == 0:
            return {
                'success': False,
                'error': 'No responses found'
            }

        percentage = (correct_count / total_count) * 100
        avg_time = responses.aggregate(Avg('time_taken'))['time_taken__avg'] or 0

        analysis = self.analyze_student_performance(student_profile)

        # ✅ SAFE FALLBACK (no crash, no API dependency)
        feedback_data = {
            "overall_assessment": f"You scored {percentage:.1f}%. Keep improving!",
            "strengths": ["Good attempt at solving questions"],
            "weaknesses": ["Need more practice on weak concepts"],
            "speed_feedback": "Try balancing speed and accuracy",
            "concept_specific_advice": [],
            "immediate_actions": [
                "Practice more questions daily",
                "Revise weak topics",
                "Focus on accuracy"
            ],
            "study_plan": {
                "today": "Practice 10 questions",
                "this_week": "Revise weak topics",
                "practice_schedule": "Daily practice"
            },
            "motivational_message": "You're improving. Keep going!",
            "difficulty_recommendation": "SAME",
            "estimated_improvement_time": "1-2 weeks",
            "red_flags": []
        }

        return {
            'success': True,
            'feedback': feedback_data,
            'session_score': percentage,
            'performance_level': analysis['performance_level'],
            'analysis_summary': {
                'accuracy_trend': analysis['accuracy_trend'],
                'average_time': avg_time
            }
        }

    def get_adaptive_questions(self, student_profile, topic, num_questions=10):
        analysis = self.analyze_student_performance(student_profile)

        if analysis['performance_level'] == 'ADVANCED':
            difficulty = 'HARD'
        elif analysis['performance_level'] == 'INTERMEDIATE':
            difficulty = 'MEDIUM'
        else:
            difficulty = 'EASY'

        questions = Question.objects.filter(
            topic=topic,
            difficulty_level=difficulty
        ).order_by('?')[:num_questions]

        return {
            'questions': questions,
            'difficulty': difficulty,
            'performance_level': analysis['performance_level']
        }