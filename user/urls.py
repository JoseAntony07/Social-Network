from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPI, LoginAPI, LogoutView, UserViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, 'user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPI.as_view(), name='user_register'),
    path('login/', LoginAPI.as_view()),
    path('logout/', LogoutView.as_view()),
]
