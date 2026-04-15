from django.db import models

# Contact Model ==========================================================
class Contact(models.Model):
    subject = models.CharField(max_length=250, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField()
    message = models.TextField()
    is_message_send = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-timestamp']



# ReplayContact Model  =============================
class ReplayContact(models.Model):
    replay = models.OneToOneField(Contact, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        ordering = ['-timestamp']