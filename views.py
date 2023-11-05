from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect,render
from django.template import loader
from django.urls import reverse
from django.contrib import messages
import datetime,re,bcrypt,validators
from .forms import SignUpForm,SignInForm,RedirectMapForm
from . import models,common_resources
from cryptography.fernet import Fernet

def start(request):
    if "signed_in" in request.session and request.session["signed_in"]==True:
        return redirect('/home/')
    return redirect('/signup/')

def signup(request):
    if common_resources.is_logged_in(request):
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
    if common_resources.is_logged_in(request):
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
                    request.session.set_expiry(172800)
                    return redirect('/home/')
                else:
                    return render(request, common_resources.signin_html, {"form": form,"messages":["Your email or password is incorrect"]}) 
    else:
        form = SignInForm()
    return render(request, common_resources.signin_html, {"form": form,"messages":[]}) 
def home(request):
    if not common_resources.is_logged_in(request):
        return redirect('/signin/')
    decr_id = common_resources.get_org_id(request)
    account = common_resources.get_user(decr_id)
    redirection_rules = common_resources.get_redirection_rules(decr_id)
    host = common_resources.host
    return render(request, common_resources.home_html, {"account":account,"redirection_rules":redirection_rules,'host':host}) 
    

def create_redirection_map(request):
    if not common_resources.is_logged_in(request):
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


def edit_redirection_map(request,rl_id):
    if not common_resources.is_logged_in(request):
        return redirect('/signin/')
    get_rule = common_resources.get_redirection_rule(rl_id)
    if (not get_rule) or get_rule[0]["org_id"] != common_resources.get_org_id(request):
        return HttpResponse('<html><head><title>Error</title></head><body><p>Something went wrong<p></body></html>')
    if request.method == "POST":
        rule_name = request.POST["rule_name"]
        rule_name = rule_name.strip()
        redirect_to = request.POST["redirect_to_url"]
        redirect_to = redirect_to.strip()
        
        #validate the url
        if not validators.url(redirect_to):
            response = 'Either this url is not valid or you did not use http/https'
            return render(request, common_resources.edit_redirection_map_html,{"rule":get_rule[0],"response":response}) 
        rule = models.RedirectMap.objects.get(id=get_rule[0]["id"])
        rule.redirect_name = rule_name
        rule.redirect_to = redirect_to
        rule.save()
        response = "Your rule has been changed"
        get_rule = common_resources.get_redirection_rule(get_rule[0]["id"])
        return render(request, common_resources.edit_redirection_map_html,{"rule":get_rule[0],"response":response}) 

    return render(request, common_resources.edit_redirection_map_html,{"rule":get_rule[0],"response":""}) 


def delete_redirection_map(request,rl_id):
    if "signed_in" not in request.session or request.session["signed_in"]==False:
        return redirect('/signin/')
    message = ""
    get_rule = common_resources.get_redirection_rule(rl_id)
    if not get_rule:
        message = "This rule does not exist"
    else:
        if get_rule[0]["org_id"] != common_resources.get_org_id(request):
            message = "You're trying to delete a wrong rule"
        else:
            rule = models.RedirectMap.objects.get(id=rl_id)
            rule.delete()
            message = "This rule has been deleted"
    return render(request, common_resources.delete_redirection_map_html, {"message":message}) 

def main_redirection(request,short_code):
    short_code = short_code.split('-')
    org_alias,randcode = short_code[0],short_code[1]
    get_rule = models.RedirectMap.objects.filter(org_alias=org_alias,randcode=randcode).values()
    if not get_rule:
        return HttpResponse('<html><head><title>Error</title></head><body><p>Something went wrong. We can not find any redirection rule for this url.<p></body></html>')
    return HttpResponseRedirect(get_rule[0]["redirect_to"])

def signout(request):
    del request.session["signed_in"]
    del request.session["fk"]
    del request.session["sk"]
    return redirect('/signin/')