from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from accounts.models import User


class ObjectViewed(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=220, blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.content_object} viewed"


class UserSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=220, blank=True, null=True)
    session_key = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    ended = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def end_session(self):
        try:
            Session.objects.get(pk=self.session_key).delete()
        except Session.DoesNotExist:
            pass

        self.active = False
        self.ended = True
        self.save()