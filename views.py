from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.template import loader
from django.urls import reverse
from django.contrib import messages
import datetime,re,bcrypt
from .forms import SignUpForm,SignInForm
from . import models,common_resources
from cryptography.fernet import Fernet

def start(request):
    user_id = request.COOKIES.get('short_url_i')
    redirect_to = current_datetime
    if not user_id:
        return redirect('/signup/')
    return redirect('/signin/')

def signup(request):
    if "signed_in" in request.session and request.session["signed_in"]==True:
        return redirect('/home/')
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            org_email = form.cleaned_data["org_email"]
            org_alias = form.cleaned_data["org_alias"]
            org_alias = org_alias.upper()
            password = form.cleaned_data["password"]
            hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

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
                return render(request, common_resources.signup_html, {"form": form,"messages":[view_response]})
            else:
                object_ = models.Org(org_email=org_email,org_alias=org_alias,password=hashed_password)
                object_.save()
                return render(request, common_resources.signup_html, {"form": form,"messages":["Your account has been created. Please visit the sign in page"]}) 
    else:
        form = SignUpForm()
    return render(request, common_resources.signup_html, {"form": form,"messages":[]})

def signin(request):
    if "signed_in" in request.session and request.session["signed_in"]==True:
        return redirect('/home/')
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            org_email = form.cleaned_data["org_email"]
            password = form.cleaned_data["password"]
            user_count = models.Org.objects.filter(org_email=org_email).count()
            if user_count<1:
                return render(request, common_resources.signin_html, {"form": form,"messages":["We can't find this account"]}) 
            else:
                user_query = models.Org.objects.filter(org_email=org_email).values()
                password_match = bcrypt.checkpw(password.encode('utf-8'), user_query[0]['password']) 
                if password_match:
                    key = Fernet.generate_key()
                    fernet = Fernet(key)
                    encrypted_id = fernet.encrypt(str(user_query[0]['id']).encode())
                    request.session["signed_in"] = True
                    request.session["fk"] = key.decode()
                    request.session["sk"] = encrypted_id.decode()
                    request.session.set_expiry(120)
                    return redirect('/home/')
                else:
                    return render(request, common_resources.signin_html, {"form": form,"messages":["Your email or password is incorrect"]}) 
    else:
        form = SignInForm()
    return render(request, common_resources.signin_html, {"form": form,"messages":[]}) 
def home(request):
    if "signed_in" not in request.session or request.session["signed_in"]==False:
        return redirect('/signin/')
    
    decr_id = common_resources.get_org_id(request)
    account = models.Org.objects.filter(id=decr_id).values()
    redirection_rules = models.RedirectMap.objects.filter(id=decr_id).values()
    return render(request, common_resources.home_html, {"account":account[0],"redirection_rules":redirection_rules}) 
    

def create_redirection_map(request):
    if "signed_in" not in request.session or request.session["signed_in"]==False:
        return redirect('/signin/')
    decr_id = common_resources.get_org_id(request)
    account = models.Org.objects.filter(id=decr_id).values()
    return render(request, common_resources.create_redirection_map_html, {"account":account[0]}) 

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