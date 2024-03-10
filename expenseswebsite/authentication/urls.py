from .views import RegistrationView,UserNameValidationView, EmailValidationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register',RegistrationView.as_view(),name="register"),
    path('validate-username',csrf_exempt(UserNameValidationView.as_view()),name="validate-username"),
    path('validate-email',csrf_exempt(EmailValidationView.as_view()),name="validate-email"),
]