from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Exam(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField() # in minutes
    total_marks = models.IntegerField(default=0)
    passing_marks = models.IntegerField(default=40)
    
    def __str__(self):
        return self.title
    
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField()

    def __str__(self):
        return self.question_text
    

 

from django.contrib.auth.models import User

class Result(models.Model):
  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    status = models.CharField(max_length=10)
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(default=timezone.now)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.score}"
   
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} - {self.exam.title}"
    

class UserAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField()

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    # RENAMED TO MATCH YOUR ADMIN PANEL
    roll_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    batch = models.CharField(max_length=100, default="BCA") # This is where you typed 'BCA'
    year = models.CharField(max_length=10, default="2026") 
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    authority_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


