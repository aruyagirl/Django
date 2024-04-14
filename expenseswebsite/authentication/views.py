from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages, auth
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
import threading

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
        
    def run(self):
        self.email.send(fail_silently=False)
    

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
                user.is_active= False
                user.save()
                
                # path_to_view
                
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs=
                             {'uidb64': uidb64, 'token': token_generator.make_token(user)})
                
                activate_url='http://'+domain+link
                
                email_subject='Activate your account'
                email_body='Hi '+user.username+ ' :Please click on the link to verify your account\n' + activate_url
                
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@expensewebsite.com',
                    [email],
                )
                
                EmailThread(email).start()
                messages.success(request,"Contratulations! Welcome to your personal financial command center!")
                return render(request,'authentication/register.html')
            
        return render(request,'authentication/register.html')

    
class VerificationView(View):
    def get(self,request,uidb64,token):
        
        try:
            id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)
            
            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            
            messages.success(request,'Account activated successfully') 
            return redirect('login')
                    
        except Exception as exception:
            pass
        

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self,request):
        username=request.POST['username']
        password=request.POST['password']
        
        if username and password:
            user=auth.authenticate(username=username, password=password)
            
            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome, '+user.username+' ,you are now logged in')
                
                    return redirect('expenses')
                    
                messages.error(request,'Account is not active, please check your email')
                return render(request, 'authentication/login.html')
            
            messages.error(request,'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
           
        messages.error(request,'Please fill in all fields')
        return render(request, 'authentication/login.html')         

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request,'You have been logged out')
        return redirect('login')
    
class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST.get("email")  
        
        try:
            validate_email(email)  
            user = User.objects.filter(email=email).first()
            if user:
                current_site = get_current_site(request)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = PasswordResetTokenGenerator().make_token(user)
                
                link = reverse('reset-user-password', kwargs={'uidb64': uidb64, 'token': token})
                reset_url = request.build_absolute_uri(link) 
                
                email_subject = 'Password Reset Requested'
                email_body = f"Hi, please use the link below to reset your password: \n{reset_url}"
                email = EmailMessage(email_subject, email_body, 'noreply@yourdomain.com', [email])
                
                # Start a separate thread to send the email
                EmailThread(email).start() 
                
                # Inform the user that reset instructions will be sent shortly
                messages.success(request, "We've emailed you instructions for setting your password. Check your inbox shortly.")
            else:
                # If no user with the provided email exists
                messages.info(request, "If an account exists with the email you entered, we've sent a password reset link.")
        except ValidationError:
            # Handle invalid email format
            messages.error(request, "Please supply a valid email.")
        
        # Redirect or render the reset-password template based on the request
        return render(request, 'authentication/reset-password.html')
class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            context = {'uidb64': uidb64, 'token': token}
            return render(request, 'authentication/set-new-password.html', context)
        else:
            messages.error(request, "The password reset link was invalid, possibly because it has already been used.")
            return redirect('request-password')

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'authentication/set-new-password.html', context)
        
        if len(password) < 6:
            messages.error(request, "Password is too short, minimum length is 6 characters.")
            return render(request, 'authentication/set-new-password.html', context)
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully.")
            return redirect('login')
        else:
            messages.error(request, "The password reset link was invalid, possibly because it has already been used.")
            return render(request, 'authentication/set-new-password.html', context)
