from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Subject, Topic, Concept
from .serializers import SubjectSerializer, TopicSerializer, ConceptSerializer

class SubjectListView(generics.ListAPIView):
    """
    List all subjects (with optional filtering)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSerializer
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True)
        
        # Optional filters
        board = self.request.query_params.get('board', None)
        grade = self.request.query_params.get('grade', None)
        
        if board:
            queryset = queryset.filter(board=board)
        if grade:
            queryset = queryset.filter(grade=grade)
        
        return queryset


class SubjectDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific subject with all topics
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSerializer
    queryset = Subject.objects.filter(is_active=True)


class TopicListView(generics.ListAPIView):
    """
    List topics for a specific subject
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSerializer
    
    def get_queryset(self):
        subject_id = self.kwargs['subject_id']
        return Topic.objects.filter(subject_id=subject_id).order_by('order')


class TopicDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific topic with all concepts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()


class ConceptListView(generics.ListAPIView):
    """
    List concepts for a specific topic
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConceptSerializer
    
    def get_queryset(self):
        topic_id = self.kwargs['topic_id']
        return Concept.objects.filter(topic_id=topic_id)