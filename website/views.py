from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse

# Forms File
from .forms import loginForm, registerForm, EditProfileForm

# Tokens File
from .tokens import account_activation_token


# DATABASE ACCESS
from django.db import connection

# MODELS
from .models import QueryResult


def home(request):
    return render(request, 'website/home.html', )

@login_required()
def dashboard(request):
    return render(request, 'website/dashboard.html')

def login_user(request):
    if request.method!= 'POST':
        form = loginForm()
    else:
        form = loginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username = form.cleaned_data['username'], password = form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.warning(request, 'Username/Email or password may have been entered incorrectly.')
                return redirect('login')
    
    return render(request, 'website/login.html', {'form' : form})

def logout_user(request):
    logout(request)
    return redirect('home')

def register_user(request):
    if request.method!='POST':
        form = registerForm()
    else:
        form = registerForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data['password2'])
            user.email = form.cleaned_data['email']
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('website/acc_active_email.html', {
                'user':user, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'website/acc_active_email_confirm.html')
    context= {
        'form' : form,
    }
    return render(request, 'website/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')



@login_required()
def edit_profile(request):
    if request.method!='POST':
        form = EditProfileForm(instance = request.user)
    else:
        form = EditProfileForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated successfully.")
            return redirect('dashboard')
    context={
        'form': form
    }
    return render(request, 'website/edit_profile.html',context)


@login_required()
def change_password(request):
    if request.method!='POST':
        form = PasswordChangeForm(user = request.user)
    else:
        form = PasswordChangeForm(data = request.POST, user = request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password has been updated successfully.")
            return redirect('dashboard')
    context={
        'form': form
    }
    return render(request, 'website/change_password.html' ,context )


@login_required
def mySQL_view(request):
    if request.method == "POST" : 
        columns = []
        # print(connection.cursor())
        try:
            with connection.cursor() as cursor:
                # print(cursor.execute("select * from fruit"))
                # print(connection.queries)
                obj, created = QueryResult.objects.get_or_create(user=request.user, query= request.POST["sql_query"])
                cursor.execute(request.POST["sql_query"])
                # print(cursor.description)
                columns = [col[0] for col in cursor.description]
                # print(columns)
                # print(dict(zip(columns, row)))
                row = cursor.fetchall()
                # print([dict(zip(columns, row)) for row in cursor.fetchall()])
        except:
            row = None
        # print(list(row))
        context={
            'queryTitle' : request.POST.get("sql_query", "None") ,
            'results' : row,
            'results_columns': columns,
            'page_load': True
        }
        return render(request, "website/Query_page.html", context )
    return render(request, "website/Query_page.html", {'page_load': False})

@login_required
def savedQuery_View(request):
    mySelfQueries = QueryResult.objects.filter(user=request.user)
    Queries = QueryResult.objects.exclude(user=request.user)
    context={
        'mySelfQueries': mySelfQueries,
        'Queries':Queries
    }
    return render(request, 'website/saved_query.html', context)