from django.db import models
from academics.models import Topic, Concept
from accounts.models import User

class Question(models.Model):
    """
    Question bank for assessments
    """
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TRUE_FALSE', 'True/False'),
        ('SHORT_ANSWER', 'Short Answer'),
        ('LONG_ANSWER', 'Long Answer'),
        ('NUMERICAL', 'Numerical'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    marks = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"


class Answer(models.Model):
    """
    Answers for questions (especially for MCQs)
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers'

    def __str__(self):
        return f"{self.question.id} - {self.answer_text[:30]}"