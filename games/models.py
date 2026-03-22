from django.db import models
from students.models import StudentProfile
from academics.models import Subject, Topic
from questions.models import Question

class Game(models.Model):
    """
    Metadata about the Unity games
    """
    name = models.CharField(max_length=100)  # e.g., "Math Adventure"
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_levels = models.IntegerField(default=3)
    unity_game_id = models.CharField(max_length=50, unique=True)  # ID Unity uses
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'games'

    def __str__(self):
        return self.name


class GameSession(models.Model):
    """
    Game session tracking
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)# Add this line
    game_level = models.IntegerField(default=1)  # Add this line (Level 1, 2, or 3)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='game_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    total_questions = models.IntegerField(default=0)
    questions_attempted = models.IntegerField(default=0)

    class Meta:
        db_table = 'game_sessions'
        ordering = ['-session_start']

def __str__(self):
    try:
        game_name = self.game.name if self.game else "No Game"
        student_name = self.student.full_name if self.student else "Unknown Student"
        return f"{student_name} - {game_name} - Level {self.game_level}"
    except:
        return f"GameSession {self.id}"


class StudentResponse(models.Model):
    """
    Individual student responses to questions
    """
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    time_taken = models.IntegerField(help_text="Time in seconds")
    ai_validation_result = models.JSONField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_responses'

    def __str__(self):
        return f"Session {self.game_session.id} - Q{self.question.id}"


class Score(models.Model):
    """
    Score tracking for each game session
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='scores')
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='score')
    total_score = models.DecimalField(max_digits=6, decimal_places=2)
    max_possible_score = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scores'

    def __str__(self):
        return f"{self.student.full_name} - {self.percentage}%"


class Feedback(models.Model):
    """
    AI-generated feedback for students
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='feedbacks')
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE, related_name='feedback')
    ai_feedback = models.TextField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedbacks'

    def __str__(self):
        return f"Feedback for {self.student.full_name} - Session {self.game_session.id}"
    
# In UnityGame model, update GAME_TYPES:

GAME_TYPES = [
    ('ZOMBIE_SURVIVAL', 'Zombie Quiz Survival'),  # NEW GAME 1
    ('MATCH_3', 'Match-3 Brain Blast'),
    ('HIDDEN_OBJECTS', 'Mystery Mansion Hunt'),
    ('SPACE_IMPOSTOR', 'Space Impostor Quiz'),
    ('ESCAPE_LAB', 'Escape Lab Challenge'),
]