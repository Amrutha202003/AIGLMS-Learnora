from rest_framework import serializers
from .models import Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'is_correct', 'explanation']
        # Hide is_correct when sending to students
        extra_kwargs = {
            'is_correct': {'write_only': True}
        }


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    concept_name = serializers.CharField(source='concept.name', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'topic', 'topic_name', 'concept', 'concept_name', 
                  'question_text', 'question_type', 'difficulty_level', 
                  'marks', 'answers']


class QuestionForGameSerializer(serializers.ModelSerializer):
    """
    Serializer for questions in game - hides correct answers
    """
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'marks', 'options']
    
    def get_options(self, obj):
        # Return only answer text, not whether it's correct
        return [answer.answer_text for answer in obj.answers.all()]