from django.conf import settings
from django.db import models


class Person(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_profile", null=True, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, default="nil")
    bio = models.CharField(max_length=300, blank=True, default="")

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email


class Post(models.Model):
    TYPE_CHOICES = [("text", "Text"), ("image", "Image"), ("video", "Video")]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    content = models.TextField(blank=True, default="")
    image_url = models.URLField(max_length=500, blank=True, default="")
    video_url = models.URLField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.type.title()} post #{self.pk}"


class Comment(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at", "id"]


class Like(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class Save(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]


class Follow(models.Model):
    follower = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="following_links")
    following = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="follower_links")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [models.UniqueConstraint(fields=["follower", "following"], name="unique_social_follow_pair")]
