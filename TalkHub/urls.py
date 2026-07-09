# from django.contrib import admin
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import PersonViewSet, PostViewSet, CommentViewSet, LikeViewSet, SaveViewSet

# router = DefaultRouter()
# router.register(r'profiles', PersonViewSet)
# router.register(r'posts', PostViewSet)
# router.register(r'comments', CommentViewSet)
# router.register(r'likes', LikeViewSet)
# router.register(r'saves', SaveViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]

from django.contrib import admin
from django.urls import path
from .views import PersonView, SinglePersonView,PostView, SinglePostView, CommentView, SingleCommentView,LikeView,SinglePostSoftDeleteView, SingleLikeView, SaveView, SingleSaveView, SinglePersonPostView, SignUpView

urlpatterns = [

    path('Person', PersonView.as_view() , name = 'person-view'),
    path('Person/<int:id>', SinglePersonView.as_view(), name = 'single-person-view'),

    path('Post', PostView.as_view() , name = 'post-view'),
    path('Post/<int:id>', SinglePostView.as_view(), name = 'single-post-view'),
    path('Posts/<int:id>',SinglePersonPostView.as_view(), name = 'single-person-post-view'),
    path('Content/<int:id>',SinglePostSoftDeleteView.as_view(), name = 'single-post-soft-delete-view'),


    path('Comment', CommentView.as_view() , name = 'comment-view'),
    path('Comment/<int:id>', SingleCommentView.as_view(), name = 'single-comment-view'),

    path('Like', LikeView.as_view() , name = 'like-view'),
    path('Like/<int:id>', SingleLikeView.as_view(), name = 'single-like-view'),

    path('Save', SaveView.as_view() , name = 'save-view'),
    path('Save/<int:id>', SingleSaveView.as_view(), name = 'single-save-view'),

    path('SignUp', SignUpView.as_view() , name = 'signup-view')



]










