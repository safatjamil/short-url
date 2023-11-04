from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.template import loader
from django.urls import reverse
from django.contrib import messages
import datetime,re,bcrypt
from .forms import SignUpForm,SignInForm
from . import models
def start(request):
    user_id = request.COOKIES.get('short_url_i')
    redirect_to = current_datetime
    if not user_id:
        return redirect('signup/')
    return redirect('signin/')

def signup(request):
    html = "signup.html"
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            org_email = form.cleaned_data["org_email"]
            org_alias = form.cleaned_data["org_alias"]
            org_alias = org_alias.upper()
            password = form.cleaned_data["password"]
            password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())

            view_response,error_flag = "", False
            org_email_query = models.Org.objects.filter(org_email=org_email).count()
            org_alias_query = models.Org.objects.filter(org_alias=org_alias).count()
            
            if org_email_query>0:
                view_response += "This email already exists."
                error_flag = True
            if org_alias_query>0:
                view_response += "This alias is not available"
                error_flag = True
            if error_flag:
                #messages.error(request,view_response)
                #return redirect('/signup/')
                return render(request, html, {"form": form,"messages":[view_response]})
            else:
                object_ = models.Org(org_email=org_email,org_alias=org_alias,password=hashed_password)
                object_.save()
                #messages.error(request,"Your account has been created. Please visit the sign in page")
                return render(request, html, {"form": form,"messages":["Your account has been created. Please visit the sign in page"]}) 
    else:
        form = SignUpForm()
    return render(request, html, {"form": form,"messages":[]})

def signin(request):
    html = "signin.html"
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            org_email = form.cleaned_data["org_email"]
            password = form.cleaned_data["password"]
            password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password,bcrypt.gensalt())
            user_query = models.Org.objects.filter(org_email=org_email,password=hashed_password).count()
            if user_query<1:
                return render(request, html, {"form": form,"messages":["Email or password is not correct"]}) 
            else:
                return render(request, html, {"form": form,"messages":["Your account is valid"]}) 
    else:
        form = SignInForm()
    return render(request, html, {"form": form,"messages":[]}) 

def current_datetime(request,time):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def global_login(request):
    html = "<html><body>Global Login</body></html>"
    return HttpResponse(html)


def name(request):
    if request.method == "POST":
        form = SignUPForm(request.POST)
        if form.is_valid():
            
            return HttpResponseRedirect("/signin")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignUPForm()

    return render(request, "name.html", {"form": form})