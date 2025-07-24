from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class TypingPrompt(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    TIME_CHOICES = [
        ('30', '30 seconds'),
        ('60', '60 seconds'),
        ('120', '120 seconds'),
    ]

    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    total_time = models.CharField(max_length=3, choices=TIME_CHOICES, default='60')

    def __str__(self):
        return f"{self.difficulty.title()} - {self.total_time}s - {self.text[:30]}..."


    
class GameResults(models.Model):
    player = models.ForeignKey(User, null=True, blank=True)
    wpm = models.FloatField()
    accuracy = models.FloatField()
    correct_words = models.IntegerField()
    total_words = models.IntegerField()
    time_taken = models.IntegerField(default=60) 
    played_at = models.DateTimeField(auto_now_add=True)

