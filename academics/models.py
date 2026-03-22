from django.db import models

class Subject(models.Model):
    """
    Subject model for different academic subjects
    """
    name = models.CharField(max_length=100)
    board = models.CharField(max_length=10, choices=[
        ('ICSE', 'ICSE'),
        ('CBSE', 'CBSE'),
        ('STATE', 'State Board'),
    ])
    grade = models.CharField(max_length=5)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        unique_together = ('name', 'board', 'grade')
        ordering = ['name']  

    def __str__(self):
        return f"{self.name} - {self.grade} ({self.board})"


class Topic(models.Model):
    """
    Topics within a subject
    """
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'topics'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class Concept(models.Model):
    """
    Concepts within a topic
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='concepts')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return f"{self.topic.name} - {self.name}"


class StudentSubject(models.Model):
    """
    Many-to-many relationship between students and subjects
    """
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='enrolled_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'student_subjects'
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}"