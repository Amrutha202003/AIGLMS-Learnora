from rest_framework import serializers
from .models import GameSession, StudentResponse, Score, Feedback
from questions.serializers import QuestionForGameSerializer

class GameSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = GameSession
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 
                  'topic', 'topic_name', 'session_start', 'session_end', 
                  'status', 'total_questions', 'questions_attempted']
        read_only_fields = ['id', 'session_start']


class GameSessionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new game session
    """
    class Meta:
        model = GameSession
        fields = ['student', 'subject', 'topic', 'total_questions']


class StudentResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = StudentResponse
        fields = ['id', 'game_session', 'question', 'question_text', 
                  'student_answer', 'is_correct', 'time_taken', 
                  'ai_validation_result', 'submitted_at']
        read_only_fields = ['id', 'is_correct', 'ai_validation_result', 'submitted_at']


class ScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Score
        fields = ['id', 'student', 'student_name', 'game_session', 
                  'total_score', 'max_possible_score', 'percentage', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'student', 'student_name', 'game_session', 
                  'ai_feedback', 'strengths', 'weaknesses', 
                  'recommendations', 'created_at']
        read_only_fields = ['id', 'created_at']