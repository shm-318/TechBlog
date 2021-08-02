from django.http.response import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from .forms import *
from django.views.generic import View
from .models import *
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
    )
from django.contrib.auth import (
                                    authenticate, 
                                    login, 
                                    logout, 
                                    get_user_model,
                                )
from django.contrib import messages
from django.urls import reverse_lazy


from .forms import TestForm
from .models import Post


class PostUpdate(View):
    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        bound_form = TestForm(instance=post)
        return render(request, 'blog/post_update.html', {'form': bound_form, 'post': post})

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        bound_form = TestForm(request.POST, instance=post)

        if bound_form.is_valid():
            new_post = bound_form.save()
            return redirect('blog:post_detail',pk)
        return render(request, 'blog/post_update.html', {'form': bound_form, 'post': post})


class PostView(View):
    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        return render(request, 'blog/post_view.html', {'post': post})


#! for confirmation mail
from .forms import UserForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
#from django.contrib.auth.models import User
from django.core.mail import EmailMessage


User = get_user_model()

# for signup user

def signup(request):
    
    if request.method == 'POST':
        print("enter in post")
        form = UserForm(request.POST)
        if form.is_valid():
            print("enter at before mail")
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            print(current_site.id)
            #for checking
            print(user,current_site.domain,urlsafe_base64_encode(force_bytes(user.pk)),account_activation_token.make_token(user))
            
            mail_subject = 'Activate your GeekENV account.'
            message = render_to_string('authentication/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            form = UserForm(request.POST)
            return render(request, 'authentication/register_s.html', {'form': form})
    else:
        form = UserForm()
        return render(request, 'authentication/register_s.html', {'form': form})

# activate function used in signup

def activate(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')




class ProfileView(View):
    template_name_auth = 'authentication/auth_user.html'
    template_name_anon = 'authentication/anon_user.html'

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            return HttpResponse('<h1>This User does not exist.</h1>')

        
        if username == request.user.username:
            context = { 'user': user }
            return render(request, self.template_name_auth, context=context)
        else:
            context = { 'user': user }
            return render(request, self.template_name_anon, context=context)
        


def Signin(request, *args, **kwargs):

    if request.method == 'POST':
        email_username = request.POST.get('email_username')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(username=email_username)
            email = user_obj.email
        except Exception as e:
            email = email_username 
        user = authenticate(request, username=email_username, password=password)
            
        if user is None:
            messages.error(request, 'Invalid Login.', extra_tags="error")
            return redirect('blog:signin') 
        
        
        login(request, user)
        
        #messages.success(request, 'Thanks for Login.', extra_tags='success')
        return redirect('blog:profile_view',request.user.username)
    return render(request,'blog/login.html') 

def IndexView(request):
    if request.user.is_authenticated:
        return redirect('blog:profile_view',request.user.username)
    return render(request,'blog/lead.html')

def Signout(request):
    logout(request)
    return redirect('blog:index_view')

def contact(request):
    form1 = ContactForm()

    if request.method == 'POST':
        form1 = ContactForm(request.POST)

        if form1.is_valid():
            form1.save()
            return redirect('/')
    return render(request, 'blog/contact.html', context={'form1': form1})

def about(request):
    return render(request, 'blog/about.html')


def register(request):
    email_unique=True
    password_match=True
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        username = request.POST.get('username')
        Email = request.POST.get('mail')
        phonenumber = request.POST.get('phone')
        password = request.POST.get('password1')
        confirmPassword = request.POST.get('password2')
        gender = request.POST.get('gender')
        print("Full Name : ",fullname)
        print("User Name : ",username)
        print("Email Address: ",Email)
        print("Phone Number: ",phonenumber)
        print("Password : ",password)
        print("Confirm Password: ",confirmPassword)
        print("Gender: ",gender)
        if password == confirmPassword:
            if len(User.objects.filter(email=Email)) == 0:
                User.objects.create(full_name=fullname,username=username,email=Email,phone_number=phonenumber,password=password,gender=gender)
                print("Registered Successfully....")
                return HttpResponseRedirect('/signin')
            else:
                email_unique=False
                return render(request,"blog/register.html",{'email_unique':email_unique,'password_match':password_match})
        else:
            password_match=False
            print("Password and Confirm Password does not Match..")
            return render(request,"blog/register.html",{'email_unique':email_unique,'password_match':password_match})
    return render(request,"blog/register.html",{'email_unique':email_unique,'password_match':password_match})



class PRView(PasswordResetView):
    email_template_name = 'authentication/password_reset_email.html'
    template_name = 'authentication/password_reset.html'
    success_url = reverse_lazy('blog:password_reset_done')

class PRConfirm(PasswordResetConfirmView):
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('blog:password_reset_complete')

class PRDone(PasswordResetDoneView):
    template_name = 'authentication/password_reset_done.html'
    

class PRComplete(PasswordResetCompleteView):
    template_name = 'authentication/password_reset_complete.html'
    