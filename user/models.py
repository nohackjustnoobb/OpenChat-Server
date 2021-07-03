from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


# max Avatar Size is 10MB
def maxAvatarSize(value):
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Image too large. Size should not exceed 20 MiB.')


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True, validators=[UnicodeUsernameValidator])
    is_active = models.BooleanField(default=True)
    is_dev = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[maxAvatarSize])
    friends = models.ManyToManyField('User', blank=True, related_name='friends_user')
    blocked = models.ManyToManyField('User', blank=True, related_name='blocked_user')

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return f'#{self.id} {self.username}'


class FriendRequest(models.Model):
    fromUser = models.ForeignKey(User, related_name='fromUser', on_delete=models.CASCADE, null=True)
    toUser = models.ForeignKey(User, related_name='toUser', on_delete=models.CASCADE, null=True)
    message = models.TextField(max_length=500, blank=True)
    requestDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Friend request from {self.fromUser} to {self.toUser}'
