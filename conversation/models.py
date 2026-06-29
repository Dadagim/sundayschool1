from django.db import models
from django.contrib.auth.models import User


class Programs(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False)
    program_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='program_leader')
    memory_verse = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_verse')
    song = models.ForeignKey(User, on_delete=models.CASCADE, related_name='song')
    bible_lesson = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bible_lesson')
    games = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')

    def __str__(self):
        return f'program for {self.date}'


class Announcements(models.Model):
    date = models.DateField(auto_now=True)
    message = models.TextField()
    image = models.ImageField(upload_to='announcements/', null=True, blank=True)
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_by')

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'announcement: {self.message}'


