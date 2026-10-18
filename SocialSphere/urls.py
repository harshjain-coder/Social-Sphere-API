from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from TalkHub.views import ApiRootView, CurrentUserView
urlpatterns=[path("",ApiRootView.as_view()),path("admin/",admin.site.urls),path("api/talkhub/",include("TalkHub.urls")),path("api/login/",TokenObtainPairView.as_view()),path("api/token/refresh/",TokenRefreshView.as_view()),path("api/me/",CurrentUserView.as_view())]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
