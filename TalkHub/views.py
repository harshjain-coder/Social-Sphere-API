import os
from pathlib import Path
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Follow, Like, Person, Post, Save
from .serializers import CommentSerializer, FollowCreateSerializer, FollowSerializer, LikeSerializer, PersonSerializer, PostSerializer, SaveSerializer, SignUpSerializer


def profile_for(user):
    try:
        return user.social_profile
    except Person.DoesNotExist as exc:
        raise NotFound("This account has no Social Sphere profile.") from exc


def posts_with_counts():
    return Post.objects.annotate(
        like_count=Count("like", filter=Q(like__deleted_at__isnull=True), distinct=True),
        comment_count=Count("comment", filter=Q(comment__deleted_at__isnull=True), distinct=True),
    )


def serialized_post(post):
    return PostSerializer(posts_with_counts().get(pk=post.pk)).data


def check_profile_owner(request, profile):
    return profile.user_id == request.user.id


def check_post_owner(request, post):
    return post.user_id.user_id == request.user.id


def not_owner_response():
    return Response({"detail": "You can only modify your own content."}, status=status.HTTP_403_FORBIDDEN)


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".ogv"}
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_VIDEO_UPLOAD_BYTES = 100 * 1024 * 1024


def post_payload_with_upload(request, existing_type=None):
    payload = request.data.copy()
    uploaded_file = request.FILES.get("media_file")
    post_type = payload.get("type", existing_type)

    if uploaded_file:
        if post_type not in {"image", "video"}:
            raise serializers.ValidationError({"media_file": "Uploads are only available for image and video posts."})

        extension = Path(uploaded_file.name).suffix.lower()
        is_image = post_type == "image"
        allowed = IMAGE_EXTENSIONS if is_image else VIDEO_EXTENSIONS
        max_bytes = MAX_IMAGE_UPLOAD_BYTES if is_image else MAX_VIDEO_UPLOAD_BYTES

        if extension not in allowed:
            raise serializers.ValidationError({"media_file": f"Unsupported file type. Allowed extensions: {', '.join(sorted(allowed))}."})
        if uploaded_file.size > max_bytes:
            raise serializers.ValidationError({"media_file": f"File is too large. Maximum size is {max_bytes // (1024 * 1024)} MB for {post_type} uploads."})

        content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
        expected = "image/" if is_image else "video/"
        if content_type and not content_type.startswith(expected):
            raise serializers.ValidationError({"media_file": f"Please upload a valid {post_type} file."})

        cloudinary_url = os.environ.get("CLOUDINARY_URL", "").strip()
        if cloudinary_url:
            try:
                # Render environment variables are sometimes pasted with the key
                # itself (CLOUDINARY_URL=...) or surrounded by quotes. Normalize
                # those harmless variations before handing the value to the SDK.
                if cloudinary_url.startswith("CLOUDINARY_URL="):
                    cloudinary_url = cloudinary_url.split("=", 1)[1].strip()
                cloudinary_url = cloudinary_url.strip().strip('"').strip("'")
                if not cloudinary_url.startswith("cloudinary://"):
                    raise ValueError("CLOUDINARY_URL must start with cloudinary://")

                import cloudinary
                import cloudinary.uploader

                # Cloudinary's Python SDK supports configuration through the
                # CLOUDINARY_URL environment variable. Set the normalized value
                # explicitly so the upload works even when Render stored the
                # copied value with surrounding quotes/prefix.
                os.environ["CLOUDINARY_URL"] = cloudinary_url
                cloudinary.config(secure=True)
                result = cloudinary.uploader.upload(
                    uploaded_file,
                    resource_type="image" if is_image else "video",
                    folder="social-sphere/posts",
                    allowed_formats=[x.lstrip(".") for x in allowed],
                    use_filename=False,
                )
                media_url = result.get("secure_url")
                if not media_url:
                    raise RuntimeError("Cloud upload did not return a secure URL")
            except Exception as exc:
                # Keep credentials out of API responses while leaving a useful
                # server-side message in Render logs for debugging.
                print(f"Cloudinary upload error: {type(exc).__name__}: {exc}")
                raise serializers.ValidationError({"media_file": "Upload failed. Please verify the Cloudinary configuration and try again."}) from exc
        else:
            if os.environ.get("RENDER_EXTERNAL_HOSTNAME") or os.environ.get("RENDER"):
                raise serializers.ValidationError({"media_file": "To upload files on the live site, add CLOUDINARY_URL in Render Environment settings."})
            safe_name = get_valid_filename(Path(uploaded_file.name).name)
            saved_name = default_storage.save(f"uploads/{post_type}/{safe_name}", uploaded_file)
            media_url = request.build_absolute_uri(default_storage.url(saved_name))

        payload["image_url"] = media_url if is_image else ""
        payload["video_url"] = media_url if not is_image else ""
    else:
        if post_type in {"image", "video"} and (existing_type is None or post_type != existing_type or request.method == "POST"):
            raise serializers.ValidationError({"media_file": f"Choose a {post_type} file before publishing."})
        payload.pop("image_url", None)
        payload.pop("video_url", None)
        if post_type == "text":
            payload["image_url"] = ""
            payload["video_url"] = ""

    payload.pop("media_file", None)
    return payload


class PublicReadAuthenticatedWriteMixin:
    def get_permissions(self):
        return [AllowAny()] if self.request.method in SAFE_METHODS else [IsAuthenticated()]


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "name": "Social Sphere API",
            "endpoints": {
                "signup": "/api/talkhub/SignUp",
                "login": "/api/login/",
                "me": "/api/me/",
                "people": "/api/talkhub/Person",
                "posts": "/api/talkhub/Post",
                "comments": "/api/talkhub/Comment",
                "likes": "/api/talkhub/Like",
                "saved_posts": "/api/talkhub/Save",
                "follows": "/api/talkhub/Follow",
            },
        })


class PersonView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request):
        return Response(PersonSerializer(Person.objects.all().order_by("first_name", "last_name", "id"), many=True).data)


class SinglePersonView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(PersonSerializer(get_object_or_404(Person, id=id)).data)

    def patch(self, request, id):
        person = get_object_or_404(Person, id=id)
        if not check_profile_owner(request, person):
            return not_owner_response()
        serializer = PersonSerializer(person, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        p = profile_for(request.user)
        return Response({"id": request.user.id, "username": request.user.username, "email": request.user.email, "first_name": p.first_name, "last_name": p.last_name, "bio": p.bio, "profile_id": p.id})


class PostView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request):
        posts = posts_with_counts().filter(is_deleted=False).select_related("user_id")
        post_type = request.query_params.get("type")
        search = request.query_params.get("search", "").strip()
        if post_type in {"text", "image", "video"}:
            posts = posts.filter(type=post_type)
        if search:
            posts = posts.filter(Q(content__icontains=search) | Q(user_id__first_name__icontains=search) | Q(user_id__last_name__icontains=search))
        posts = posts.order_by("-like_count", "-comment_count", "-created_at", "-id") if request.query_params.get("sort") == "trending" else posts.order_by("-created_at", "-id")
        return Response(PostSerializer(posts, many=True).data)

    def post(self, request):
        serializer = PostSerializer(data=post_payload_with_upload(request))
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user_id=profile_for(request.user))
        return Response(serialized_post(post), status=status.HTTP_201_CREATED)


class SinglePostView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(PostSerializer(get_object_or_404(posts_with_counts().filter(is_deleted=False), id=id)).data)

    def patch(self, request, id):
        post = get_object_or_404(Post, id=id, is_deleted=False)
        if not check_post_owner(request, post):
            return not_owner_response()
        serializer = PostSerializer(post, data=post_payload_with_upload(request, post.type), partial=True)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response(serialized_post(post))

    def delete(self, request, id):
        post = get_object_or_404(Post, id=id, is_deleted=False)
        if not check_post_owner(request, post):
            return not_owner_response()
        post.is_deleted = True
        post.save(update_fields=["is_deleted"])
        now = timezone.now()
        Comment.objects.filter(post_id=post, deleted_at__isnull=True).update(deleted_at=now)
        Like.objects.filter(post_id=post, deleted_at__isnull=True).update(deleted_at=now)
        Save.objects.filter(post_id=post, deleted_at__isnull=True).update(deleted_at=now)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SinglePersonPostView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(PostSerializer(posts_with_counts().filter(user_id=get_object_or_404(Person, id=id), is_deleted=False).order_by("-created_at", "-id"), many=True).data)

    def post(self, request, id):
        person = get_object_or_404(Person, id=id)
        if not check_profile_owner(request, person):
            return not_owner_response()
        serializer = PostSerializer(data=post_payload_with_upload(request))
        serializer.is_valid(raise_exception=True)
        post = serializer.save(user_id=person)
        return Response(serialized_post(post), status=status.HTTP_201_CREATED)


class SinglePostSoftDeleteView(SinglePostView):
    pass


class CommentView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request):
        comments = Comment.objects.filter(deleted_at__isnull=True).select_related("post_id", "user_id")
        post_id = request.query_params.get("post_id")
        if post_id:
            comments = comments.filter(post_id_id=post_id)
        return Response(CommentSerializer(comments, many=True).data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(user_id=profile_for(request.user))
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class SingleCommentView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(CommentSerializer(get_object_or_404(Comment, id=id, deleted_at__isnull=True)).data)

    def patch(self, request, id):
        comment = get_object_or_404(Comment, id=id, deleted_at__isnull=True)
        if not check_profile_owner(request, comment.user_id):
            return not_owner_response()
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(CommentSerializer(serializer.save()).data)

    def delete(self, request, id):
        comment = get_object_or_404(Comment, id=id, deleted_at__isnull=True)
        if not check_profile_owner(request, comment.user_id):
            return not_owner_response()
        comment.deleted_at = timezone.now()
        comment.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request):
        likes = Like.objects.filter(deleted_at__isnull=True).select_related("post_id", "user_id")
        post_id = request.query_params.get("post_id")
        user_id = request.query_params.get("user_id")
        if post_id:
            likes = likes.filter(post_id_id=post_id)
        if user_id:
            likes = likes.filter(user_id_id=user_id)
        return Response(LikeSerializer(likes, many=True).data)

    def post(self, request):
        profile = profile_for(request.user)
        inp = LikeSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        post = inp.validated_data["post_id"]
        like = Like.objects.filter(post_id=post, user_id=profile).order_by("id").first()
        if like and like.deleted_at is None:
            return Response(LikeSerializer(like).data)
        if like:
            like.deleted_at = None
            like.created_at = timezone.now()
            like.save(update_fields=["deleted_at", "created_at"])
            return Response(LikeSerializer(like).data)
        return Response(LikeSerializer(Like.objects.create(post_id=post, user_id=profile)).data, status=status.HTTP_201_CREATED)


class SingleLikeView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(LikeSerializer(get_object_or_404(Like, id=id, deleted_at__isnull=True)).data)

    def delete(self, request, id):
        like = get_object_or_404(Like, id=id, deleted_at__isnull=True)
        if not check_profile_owner(request, like.user_id):
            return not_owner_response()
        like.deleted_at = timezone.now()
        like.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SaveView(PublicReadAuthenticatedWriteMixin, APIView):
    def get_permissions(self):
        return [IsAuthenticated()]

    def get(self, request):
        saves = Save.objects.filter(deleted_at__isnull=True, user_id=profile_for(request.user)).select_related("post_id", "user_id")
        post_id = request.query_params.get("post_id")
        if post_id:
            saves = saves.filter(post_id_id=post_id)
        return Response(SaveSerializer(saves, many=True).data)

    def post(self, request):
        profile = profile_for(request.user)
        inp = SaveSerializer(data=request.data)
        inp.is_valid(raise_exception=True)
        post = inp.validated_data["post_id"]
        saved = Save.objects.filter(post_id=post, user_id=profile).order_by("id").first()
        if saved and saved.deleted_at is None:
            return Response(SaveSerializer(saved).data)
        if saved:
            saved.deleted_at = None
            saved.created_at = timezone.now()
            saved.save(update_fields=["deleted_at", "created_at"])
            return Response(SaveSerializer(saved).data)
        return Response(SaveSerializer(Save.objects.create(post_id=post, user_id=profile)).data, status=status.HTTP_201_CREATED)


class SingleSaveView(PublicReadAuthenticatedWriteMixin, APIView):
    def get_permissions(self):
        return [IsAuthenticated()]

    def get(self, request, id):
        saved = get_object_or_404(Save, id=id, deleted_at__isnull=True)
        if not check_profile_owner(request, saved.user_id):
            return not_owner_response()
        return Response(SaveSerializer(saved).data)

    def delete(self, request, id):
        saved = get_object_or_404(Save, id=id, deleted_at__isnull=True)
        if not check_profile_owner(request, saved.user_id):
            return not_owner_response()
        saved.deleted_at = timezone.now()
        saved.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request):
        follows = Follow.objects.select_related("follower", "following")
        follower_id = request.query_params.get("follower_id")
        following_id = request.query_params.get("following_id")
        if follower_id:
            follows = follows.filter(follower_id=follower_id)
        if following_id:
            follows = follows.filter(following_id=following_id)
        return Response(FollowSerializer(follows, many=True).data)

    def post(self, request):
        profile = profile_for(request.user)
        serializer = FollowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following = serializer.validated_data["following_id"]
        if following.id == profile.id or following.user_id == request.user.id:
            return Response({"following_id": ["You cannot follow yourself."]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            follow, created = Follow.objects.get_or_create(follower=profile, following=following)
        except IntegrityError:
            follow = Follow.objects.get(follower=profile, following=following)
            created = False
        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SingleFollowView(PublicReadAuthenticatedWriteMixin, APIView):
    def get(self, request, id):
        return Response(FollowSerializer(get_object_or_404(Follow, id=id)).data)

    def delete(self, request, id):
        follow = get_object_or_404(Follow, id=id)
        if not check_profile_owner(request, follow.follower):
            return not_owner_response()
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = profile_for(user)
        return Response({"message": "User registered successfully.", "username": user.username, "email": user.email, "profile_id": profile.id}, status=status.HTTP_201_CREATED)
