from rest_framework import serializers
from .models import Subject, Topic, Concept, StudentSubject

class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ['id', 'name', 'description', 'learning_objectives']


class TopicSerializer(serializers.ModelSerializer):
    concepts = ConceptSerializer(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'order', 'difficulty_level', 'concepts']


class SubjectSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'board', 'grade', 'description', 'is_active', 'topics']


class SubjectListSerializer(serializers.ModelSerializer):
    """
    Lighter serializer for listing subjects without nested data
    """
    class Meta:
        model = Subject
        fields = ['id', 'name', 'board', 'grade', 'description']


class StudentSubjectSerializer(serializers.ModelSerializer):
    subject_details = SubjectListSerializer(source='subject', read_only=True)
    
    class Meta:
        model = StudentSubject
        fields = ['id', 'subject', 'subject_details', 'enrolled_at', 'is_active']