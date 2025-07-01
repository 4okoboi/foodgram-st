from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from storages.backends.s3boto3 import S3Boto3Storage

class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True, storage=S3Boto3Storage())
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    load_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def clean(self):
        if self.subscriber == self.author:
            raise ValidationError("Can't subscribe to yourself")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subscriber.username} subscribed on {self.author.username}"