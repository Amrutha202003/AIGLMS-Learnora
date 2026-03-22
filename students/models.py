from django.db import models
from accounts.models import User

class StudentProfile(models.Model):
    """
    Student profile with academic information
    """
    BOARD_CHOICES = [
        ('ICSE', 'ICSE'),
        ('CBSE', 'CBSE'),
        ('STATE', 'State Board'),
    ]
    
    GRADE_CHOICES = [
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12'),
        ('UG', 'Under Graduate'),
        ('PG', 'Post Graduate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=200)
    board = models.CharField(max_length=10, choices=BOARD_CHOICES)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
    profile_image = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.full_name} - {self.grade} ({self.board})"
    
class PlayerScore(models.Model):
 
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='player_score')
    total_score = models.IntegerField(default=1000)  # Starting score
    games_played = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)
    total_wrong_answers = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # in seconds
    average_accuracy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'player_scores'
    
    def __str__(self):
        return f"{self.student.full_name} - {self.total_score} points"
    
    def update_score(self, points_change, is_correct, time_taken):
        """
        Update score based on game performance
        """
        self.total_score += points_change
        self.games_played += 1
        self.total_time_spent += time_taken
        
        if is_correct:
            self.total_correct_answers += 1
        else:
            self.total_wrong_answers += 1
        
        # Calculate accuracy
        total_attempts = self.total_correct_answers + self.total_wrong_answers
        if total_attempts > 0:
            self.average_accuracy = (self.total_correct_answers / total_attempts) * 100
        
        self.save()
    