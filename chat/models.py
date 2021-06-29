from django.db import models
from user.models import User
from django.core.exceptions import ValidationError


# max file size is 20MB
def maxFileSize(value):
    limit = 20 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 20 MiB.')


# max Image Size is 10MB
def maxImageSize(value):
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Image too large. Size should not exceed 10 MiB.')


class Group(models.Model):
    createDate = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    isDM = models.BooleanField()
    members = models.ManyToManyField(User, related_name='members')
    groupName = models.TextField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    groupAdmin = models.ManyToManyField(User, related_name='groupAdmin')
    pinnedMessage = models.ManyToManyField('Message', blank=True)

    def __str__(self):
        return f'#{self.id} {self.groupName}'


class Message(models.Model):
    sendDateTime = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=5000, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='owner', null=True)
    sentGroup = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sentGroup')
    additionFile = models.FileField(upload_to='files/', blank=True, validators=[maxFileSize])
    additionImage = models.ImageField(upload_to='images/', blank=True, validators=[maxImageSize])
    MemberRead = models.ImageField(default=0)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.owner.username}'
