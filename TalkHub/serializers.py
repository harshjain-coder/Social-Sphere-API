from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import Comment, Follow, Like, Person, Post, Save

User = get_user_model()

class PersonSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    class Meta:
        model = Person
        fields = ["id", "first_name", "last_name", "username", "bio"]
        read_only_fields = ["id", "username"]
    def get_username(self, obj):
        return obj.user.username if obj.user_id else None

class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True, required=False)
    comment_count = serializers.IntegerField(read_only=True, required=False)
    class Meta:
        model = Post
        fields = ["id", "type", "user_id", "content", "image_url", "video_url", "created_at", "is_deleted", "like_count", "comment_count"]
        read_only_fields = ["id", "user_id", "created_at", "is_deleted", "like_count", "comment_count"]
    def validate(self, attrs):
        post_type = attrs.get("type", getattr(self.instance, "type", None))
        content = attrs.get("content", getattr(self.instance, "content", "")) or ""
        image_url = attrs.get("image_url", getattr(self.instance, "image_url", "")) or ""
        video_url = attrs.get("video_url", getattr(self.instance, "video_url", "")) or ""
        if post_type == "text" and not content.strip():
            raise serializers.ValidationError({"content": "Text posts need some content."})
        if post_type == "image" and not image_url.strip():
            raise serializers.ValidationError({"image_url": "An uploaded image is required."})
        if post_type == "video" and not video_url.strip():
            raise serializers.ValidationError({"video_url": "An uploaded video is required."})
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "post_id", "user_id", "content", "created_at", "deleted_at"]
        read_only_fields = ["id", "user_id", "created_at", "deleted_at"]
    def validate_content(self, value):
        value = value.strip()
        if not value: raise serializers.ValidationError("Comment cannot be empty.")
        return value
    def validate_post_id(self, value):
        if value.is_deleted: raise serializers.ValidationError("This post is no longer available.")
        return value

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "post_id", "user_id", "created_at", "deleted_at"]
        read_only_fields = ["id", "user_id", "created_at", "deleted_at"]
    def validate_post_id(self, value):
        if value.is_deleted: raise serializers.ValidationError("This post is no longer available.")
        return value

class SaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Save
        fields = ["id", "post_id", "user_id", "created_at", "deleted_at"]
        read_only_fields = ["id", "user_id", "created_at", "deleted_at"]
    def validate_post_id(self, value):
        if value.is_deleted: raise serializers.ValidationError("This post is no longer available.")
        return value

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = fields

class FollowCreateSerializer(serializers.Serializer):
    following_id = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())

class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    def validate_username(self, value):
        value = value.strip()
        if not value: raise serializers.ValidationError("Username is required.")
        if User.objects.filter(username__iexact=value).exists(): raise serializers.ValidationError("Username is already taken.")
        return value
    def validate_password(self, value):
        candidate_user = User(username=self.initial_data.get("username", ""), email=self.initial_data.get("email", ""), first_name=self.initial_data.get("first_name", ""), last_name=self.initial_data.get("last_name", ""))
        validate_password(value, user=candidate_user)
        return value
    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists(): raise serializers.ValidationError("Email is already registered.")
        if Person.objects.filter(email__iexact=value, user__isnull=False).exists(): raise serializers.ValidationError("Email is already registered.")
        return value
    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"]
        first_name = validated_data["first_name"].strip()
        last_name = validated_data["last_name"].strip()
        user = User.objects.create_user(password=password, **validated_data)
        profile = Person.objects.filter(email__iexact=email, user__isnull=True).first()
        if profile:
            profile.user = user; profile.first_name = first_name; profile.last_name = last_name; profile.email = email
            profile.save(update_fields=["user", "first_name", "last_name", "email"])
        else:
            Person.objects.create(user=user, first_name=first_name, last_name=last_name, email=email)
        return user
