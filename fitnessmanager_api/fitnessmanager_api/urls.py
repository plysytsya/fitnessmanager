"""
URL configuration for fitnessmanager_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import re_path
from .views import customer_views, message_views

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path("admin/", admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/profile_picture/", customer_views.GetProfilePicture.as_view(), name="profile_picture"),
    re_path(r'^customer-data/?$', customer_views.CustomerData.as_view(), name='customer_data'),
    path('messages/customer/unread_count/', message_views.UnreadMessageCountView.as_view()),
    path('messages/customer/sent/', message_views.SentMessageView.as_view()),
    path('messages/customer/inbox/', message_views.InboxView.as_view()),
    path('messages/customer/<int:message_id>/', message_views.MessageDetailView.as_view()),
    path('messages/customer/send/', message_views.SendMessageView.as_view()),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
