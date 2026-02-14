from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatThread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @classmethod
    def get_or_create_thread(cls, user1, user2):
        if user1 == user2:
            return None
        
        threads = cls.objects.filter(participants=user1).filter(participants=user2)
        if threads.exists():
            return threads.first()
        
        thread = cls.objects.create()
        thread.participants.add(user1, user2)
        return thread

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Status flags for ticks
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Media support
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    # CRUD support
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def mark_as_delivered(self):
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save()

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            if not self.is_delivered:
                self.is_delivered = True
                self.delivered_at = self.read_at
            self.save()

    def __str__(self):
        return f"From {self.sender} at {self.timestamp}"
