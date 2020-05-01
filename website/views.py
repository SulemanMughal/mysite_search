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
from django.utils import timezone
from django.http import JsonResponse
from django.http import JsonResponse
from django.core import serializers
from django.contrib.admin.models import ADDITION, LogEntry, CHANGE ,DELETION
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
# Forms File
from .forms import loginForm, registerForm, EditProfileForm, configurationRulesForm, ColorRangeForm

# Tokens File
from .tokens import account_activation_token


# DATABASE ACCESS
from django.db import connection

# MODELS
from .models import QueryResult,configurationRules, configResultsDataBase, ColorRange
from django.db.models import Count
from django.db.models.query import QuerySet
from decimal import Decimal


# Printing Objects
def printObjects(x):
    print("**********************************************************")
    print("**********************************************************")
    # for i in x.__dict__:
    # # print(x.__dict__)
    #     print(i, "  :  ", x.__dict__[i])
    print(x)
    print("**********************************************************")
    print("**********************************************************")


# Create Results from Configuration Rules Form
def createResultsObjects(x):
    try:
        obj = configResultsDataBase.objects.create(
            user = x.user,
            configRules = x,
            query_store_DB_1 = x.source_query,
            results_store_DB_1 = '',
            results_store_DB_1_timestamp = x.timestamp,
            query_store_DB_2 = x.source_query,
            results_store_DB_2 = '',
            results_store_DB_2_timestamp = x.timestamp,
            updated_timtstamp = x.timestamp,
            timestamp = x.timestamp
        )
        # try:
        #     with connection.cursor() as cursor:
        #         cursor.execute(f"{obj.query_store_DB_1}")
        #         row = cursor.fetchall()
        # except:
        #     row = None
        # # printObjects(row)
        # printObjects(type(results_query_DB_1(x.source_query)))
        # printObjects(type(results_query_DB_1(x.source_query)))
        R1 = results_query_DB_1(x.source_query)[0][0]
        R2 = results_query_DB_2(x.source_query)[0][0]
        if isinstance(R1, Decimal):
            obj.results_store_DB_1 = float(R1)
        else:
            obj.results_store_DB_1 = (R1)
        obj.save()
        if isinstance(R2, Decimal):
            obj.results_store_DB_2 = float(R2)
        else:
            obj.results_store_DB_2 = (R2)
        obj.save()
        LogEntry.objects.create(
                            user = User.objects.get(
                                username = obj.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = ADDITION,
                            object_repr = str(obj.__str__()),
                            object_id = obj.id,
                            change_message = "Results has been Created"
                        
                        )
        return obj
    except Exception as e:
        print(e)
        return None


# Results For DB Query 1 at the time of configure rule creation
def results_query_DB_1(query_1):
    columns = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"{query_1}")
            row = cursor.fetchall()
    except:
        row = None
    # printObjects(row)
    return row

# Results For DB Query 2 at the time of configure rule creation
def results_query_DB_2(query_2):
    columns = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"{query_2}")
            row = cursor.fetchall()
    except:
        row = None
    # printObjects(row)
    return row

def home(request):
    return render(request, 'website/home.html' )

@login_required()
def dashboard(request):
    C  = [ ]
    D = {}
    for i in configurationRules.objects.values('header').annotate(dcount=Count('header')):
        C.append(configurationRules.objects.filter(header = i['header'],  user=User.objects.get(username=request.user.username)))
        D[i['header']] = configurationRules.objects.filter(header = i['header'], user=User.objects.get(username=request.user.username))
    configurations = {}
    for i in D:
        if len(D[i]) != 0:
            configurations[i] = D[i]
    # print("**********************************************************")
    # print(configurations)
    # if len(configurations) !=0:
    #     try:
    #         for i in configurations:
    #             # print(configurations[i])
    #             for j in configurations[i]:
    #                 print(j.get_current_object_results())
    #     except Exception as e:
    #         print(e)
            
    # print("**********************************************************")
    form = configurationRulesForm()
    form_2 = ColorRangeForm()
    if request.method == "POST":
        form = configurationRulesForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username=request.user.username)
            obj.save()
            for i in form.cleaned_data.get("color", None):
                obj.color.add(ColorRange.objects.get(id=i.id))
            obj.save()
            if createResultsObjects(obj):
                messages.success(request, "Configuration Rule has been added.")
                return redirect("dashboard")
            else:
                messages.success(request, "Results can't be obtained from that configure rules.")
                return redirect("dashboard")
        else:
            messages.success(request, str(form.errors))
            return redirect("dashboard")
    context={
        'configurations': configurations,
        'form' : form,
        'form_2': form_2
    }
    return render(request, 'website/dashboard.html', context)

@login_required()
def profile(request):
    return render(request, 'website/profile.html')

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
            return redirect('profile')
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
            return redirect('profile')
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


@login_required
def savedColorRange(request):
    if request.method != "POST":
        return redirect("dashboard")
    else:
        form = ColorRangeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = User.objects.get(username= request.user.username)
            obj.range = request.POST['range']
            obj.save()
            messages.success(request, "Result Color Range : '{query}' has been created".format(query = request.POST['range']))
            return redirect("dashboard")
        else:
            messages.error(request, str(form.errors))
            return redirect("dashboard")

        
@login_required
def updateDBResults(request):
    if request.is_ajax and request.method == "GET":
        data = request.GET.get("data", None)
        rule_id, result_id, DB_id = data.split("_")
        try:
            rule =  configurationRules.objects.get(id=int(rule_id))
            result = configResultsDataBase.objects.get(id  = int(result_id))
            if DB_id == "DB1":
                temp = results_query_DB_1(result.query_store_DB_1)[0][0]
                if isinstance(temp, Decimal):
                    result.results_store_DB_1 = float(temp)
                    result.results_store_DB_1_timestamp = timezone.now()
                    result.save()
                    LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                    messages.success(request,"Resutls has been updated.")
                    return JsonResponse({"data":result.results_store_DB_1, "valid": True, "time" : (result.results_store_DB_1_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                else:
                    result.results_store_DB_1 = (temp)
                    result.results_store_DB_1_timestamp = timezone.now()
                    result.save()
                    LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                    messages.success(request,"Resutls has been updated.")
                    return JsonResponse({"data":result.results_store_DB_1, "valid": True, "time" : (result.results_store_DB_1_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
            elif DB_id == "DB2":
                temp = results_query_DB_2(result.query_store_DB_2)[0][0]
                if isinstance(temp, Decimal):
                    result.results_store_DB_2 = float(temp)
                    result.results_store_DB_2_timestamp = timezone.now()
                    result.save()
                    LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                    messages.success(request,"Resutls has been updated.")
                    return JsonResponse({"data":result.results_store_DB_2, "valid": True, "time" : (result.results_store_DB_2_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                else:
                    result.results_store_DB_2 = (temp)
                    result.results_store_DB_2_timestamp = timezone.now()
                    result.save()
                    LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                    messages.success(request,"Resutls has been updated.")
                    return JsonResponse({"data":result.results_store_DB_2, "valid": True, "time" : (result.results_store_DB_2_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
            return JsonResponse({ "valid": True}, status = 200)
        except Exception as e:
            return JsonResponse({}, status = 400)
    return JsonResponse({}, status = 400)


@login_required
def upDateQueryDB(request):
    if request.is_ajax and request.method == "POST":
        data = request.POST.get("query", None)
        query_1 = request.POST.get("query1", None)
        if data is None:
            return JsonResponse({"error": ""}, status=400)
        else:
            rule_id,result_id,DB_id = data.split("_")
            try:
                rule =  configurationRules.objects.get(id=int(rule_id))
                result = configResultsDataBase.objects.get(id  = int(result_id))
                if DB_id == "DB1":
                    result.query_store_DB_1 = query_1
                    result.save()
                    temp = results_query_DB_1(result.query_store_DB_1)[0][0]
                    if isinstance(temp, Decimal):
                        result.results_store_DB_1 = float(temp)
                        result.results_store_DB_1_timestamp = timezone.now()
                        result.save()
                        LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                        return JsonResponse({"data":result.results_store_DB_1, "valid": True, "query":result.query_store_DB_1,  "time" : (result.results_store_DB_1_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                    else:
                        result.results_store_DB_1 = (temp)
                        result.results_store_DB_1_timestamp = timezone.now()
                        result.save()
                        LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                        return JsonResponse({"data":result.results_store_DB_1, "valid": True,  "query":result.query_store_DB_1,  "time" : (result.results_store_DB_1_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                elif DB_id == "DB2":
                    result.query_store_DB_2 = query_1
                    result.save()
                    temp = results_query_DB_2(result.query_store_DB_2)[0][0]
                    if isinstance(temp, Decimal):
                        result.results_store_DB_2 = float(temp)
                        result.results_store_DB_2_timestamp = timezone.now()
                        result.save()
                        LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                        return JsonResponse({"data":result.results_store_DB_2, "valid": True,  "query":result.query_store_DB_2,  "time" : (result.results_store_DB_2_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                    else:
                        result.results_store_DB_2 = (temp)
                        result.results_store_DB_2_timestamp = timezone.now()
                        result.save()
                        LogEntry.objects.create(
                            user = User.objects.get(
                                username = request.user.username
                            ),
                            content_type = ContentType.objects.get(
                                model = "configresultsdatabase"
                            ),
                            action_time = timezone.now(),
                            action_flag = CHANGE,
                            object_repr = str(result.__str__()),
                            object_id = result.id,
                            change_message = "Results has been updated"
                        
                        )
                        return JsonResponse({"data":result.results_store_DB_2, "valid": True,  "query":result.query_store_DB_2,  "time" : (result.results_store_DB_2_timestamp.strftime("%B %d, %Y, %I:%M %p"))}, status = 200)
                return JsonResponse({ "valid": True}, status = 200)
            except Exception as e:
                return JsonResponse({}, status = 400)
    else:
        return JsonResponse({"error": ""}, status=400)
    return JsonResponse({"error": ""}, status=400)


@login_required
def UserLogActions(request):
    template_name="website/logs_list.html"
    try:    
        # objects = LogEntry.objects.filter(user=User.objects.get(username=request.user.username))
        objects = LogEntry.objects.filter(Q(user=User.objects.get(username=request.user.username)) & Q(content_type = ContentType.objects.get(model = "configresultsdatabase")))
        context={
            'objects': objects
        }
        return render(request,
                      template_name,
                      context)

    except Exception as e:
        messages.success(request, str(e) )
        return redirect("dashboard")        
    
@login_required
def refreshQueryRow(request,configurationRules_id , configResultsDataBase_id):
    if request.method == "POST":
        try:
            rule =  configurationRules.objects.get(id=int(configurationRules_id))
            result = configResultsDataBase.objects.get(id  = int(configResultsDataBase_id))
            #Get Results direct from database and update resutlsModels
            rule.source_query = request.POST['query1']
            rule.save()
            try:
                R1 = results_query_DB_1(rule.source_query)[0][0]
                R2 = results_query_DB_2(rule.source_query)[0][0]
                result.query_store_DB_1  = rule.source_query
                result.query_store_DB_2  = rule.source_query
                result.save()
                if isinstance(R1, Decimal):
                    result.results_store_DB_1 = float(R1)
                    result.results_store_DB_1_timestamp = timezone.now()
                else:
                    result.results_store_DB_1 = (R1)
                    result.results_store_DB_1_timestamp = timezone.now()
                result.save()
                if isinstance(R2, Decimal):
                    result.results_store_DB_2 = float(R2)
                    result.results_store_DB_2_timestamp = timezone.now()
                else:
                    result.results_store_DB_2 = (R2)
                    result.results_store_DB_2_timestamp = timezone.now()
                result.save()
                LogEntry.objects.create(
                    user = User.objects.get(
                        username = request.user.username
                    ),
                    content_type = ContentType.objects.get(
                        model = "configresultsdatabase"
                    ),
                    action_time = timezone.now(),
                    action_flag = CHANGE,
                    object_repr = str(result.__str__()),
                    object_id = result.id,
                    change_message = "Results has been updated"
                
                )
                messages.success(request,"Results has been updated")
                return redirect("dashboard")
            except Exception as e:
                messages.success(request, str(e))
                return redirect("dashboard")
        except Exception as e:
            messages.success(request, str(e))
            return redirect("dashboard")
    else:
        try:
            rule =  configurationRules.objects.get(id=int(configurationRules_id))
            result = configResultsDataBase.objects.get(id  = int(configResultsDataBase_id))
            
            #Get Results direct from database and update resutlsModels
            try:
                R1 = results_query_DB_1(rule.source_query)[0][0]
                R2 = results_query_DB_2(rule.source_query)[0][0]
                result.query_store_DB_1  = rule.source_query
                result.query_store_DB_2  = rule.source_query
                result.save()
                if isinstance(R1, Decimal):
                    result.results_store_DB_1 = float(R1)
                    result.results_store_DB_1_timestamp = timezone.now()
                else:
                    result.results_store_DB_1 = (R1)
                    result.results_store_DB_1_timestamp = timezone.now()
                result.save()
                if isinstance(R2, Decimal):
                    result.results_store_DB_2 = float(R2)
                    result.results_store_DB_2_timestamp = timezone.now()
                else:
                    result.results_store_DB_2 = (R2)
                    result.results_store_DB_2_timestamp = timezone.now()
                result.save()
                messages.success(request,"Results has been updated")
                return redirect("dashboard")
                LogEntry.objects.create(
                        user = User.objects.get(
                            username = request.user.username
                        ),
                        content_type = ContentType.objects.get(
                            model = "configresultsdatabase"
                        ),
                        action_time = timezone.now(),
                        action_flag = CHANGE,
                        object_repr = str(result.__str__()),
                        object_id = result.id,
                        change_message = "Results has been updated"
                    
                    )
            except Exception as e:
                messages.success(request, str(e))
                return redirect("dashboard")
        except Exception as e:
            messages.success(request, str(e))
            return redirect("dashboard")