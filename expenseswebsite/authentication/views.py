from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages


# Create your views here.

class UserNameValidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        username=data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should only contain alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':"Username is taken! Let's brainstorm another winner"},status=409)
        return JsonResponse({'username_valid':True})
    
class EmailValidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        email=data['email']
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'email_error': 'Email is not valid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': "Looks like someone else snagged that email address first! Time to invent a new digital identity"}, status=409)
        return JsonResponse({'email_valid': True})

class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')
    
    def post(self,request):
        
        messages.success(request, 'Success')
        messages.warning(request, 'Warning')
        messages.info(request,'Info')
        messages.error(request,'Error')
        
        return render(request,'authentication/register.html')
        