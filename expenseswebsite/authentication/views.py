from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe,urlsafe_base64_encode

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

        # Get user data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        context={
            'fieldValues':request.POST
        }

        # Validate username and email
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request,'Password too short')
                    return render(request,'authentication/register.html',context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_activate= False
                user.save()
                email_subject='Activate your account'
                email_body='Test body'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@expensewebsite.com',
                    [email],
                )
                
                email.send(fail_silently=False)
                messages.success(request,"Contratulations! Welcome to your personal financial command center!")
                return render(request,'authentication/register.html')
            
        return render(request,'authentication/register.html')
        