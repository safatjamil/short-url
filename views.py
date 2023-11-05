from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.template import loader
from django.urls import reverse
from django.contrib import messages
import datetime,re,bcrypt
from .forms import SignUpForm,SignInForm,RedirectMapForm
from . import models,common_resources
from cryptography.fernet import Fernet

def start(request):
    if "signed_in" in request.session and request.session["signed_in"]==True:
        return redirect('/home/')
    return redirect('/signup/')

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
                    request.session.set_expiry(6000)
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
    account = common_resources.get_user(decr_id)
    redirection_rules = common_resources.get_redirection_rules(decr_id)
    host = common_resources.host
    return render(request, common_resources.home_html, {"account":account,"redirection_rules":redirection_rules,'host':host}) 
    

def create_redirection_map(request):
    if "signed_in" not in request.session or request.session["signed_in"]==False:
        return redirect('/signin/')
    decr_id = common_resources.get_org_id(request)
    account = common_resources.get_user(decr_id)
    if request.method == "POST":
        form = RedirectMapForm(request.POST)
        if form.is_valid():
            rule_name = form.cleaned_data["rule_name"]
            redirect_to_url = form.cleaned_data["redirect_to_url"]
            org_alias = account['org_alias']
            randcode = common_resources.gen_rand_str(5)
            counter = 0
            while counter<10:
                if models.RedirectMap.objects.filter(org_alias=org_alias,randcode=randcode).count()>0:
                    randcode = common_resources.gen_rand_str(5)
                else:
                    break
                counter+=1
            incoming_url = org_alias+"-"+randcode
            object_ = models.RedirectMap(org_id=decr_id,org_alias=org_alias,redirect_name=rule_name,incoming_url=incoming_url,randcode=randcode,redirect_to=redirect_to_url)
            object_.save()
            return redirect('/home/')
    else:
        form = RedirectMapForm()
    return render(request, common_resources.create_redirection_map_html, {"account":account,"form":form}) 

def delete_redirection_map(request,rl_id):
    if "signed_in" not in request.session or request.session["signed_in"]==False:
        return redirect('/signin/')
    message = ""
    get_rule = common_resources.get_redirection_rule(rl_id)
    if not get_rule:
        message = "This rule does not exist"
    else:
        if int(get_rule[0]["org_id"]) != common_resources.get_org_id(request):
            message = "You're trying to delete a wrong rule"
        else:
            rule = models.RedirectMap.objects.get(id=rl_id)
            rule.delete()
            message = "This rule has been deleted"
    return render(request, common_resources.delete_redirection_map_html, {"message":message}) 
    
 
    