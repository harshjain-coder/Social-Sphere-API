from django.db import models

# Create your models here.
class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True,default= "nil")

class Post(models.Model):
    type = models.CharField(max_length=10, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video')
    ])
    
    user_id = models.ForeignKey('Person', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

class Comment(models.Model):
    post_id = models.ForeignKey('Post', on_delete=models.CASCADE)
    user_id = models.ForeignKey('Person', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Like(models.Model):
    post_id = models.ForeignKey('Post', on_delete=models.CASCADE)
    user_id = models.ForeignKey('Person', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Save(models.Model):
    post_id = models.ForeignKey('Post', on_delete=models.CASCADE)
    user_id = models.ForeignKey('Person', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class SignUp(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True,default= "nil")
    password = models.CharField(max_length=30)



