from cryptography.fernet import Fernet
from . import models
import random

# attributes
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
randcode_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
host = 'shafat.com'

#html
signup_html = 'signup.html'
signin_html = 'signin.html'
home_html = 'home.html'
create_redirection_map_html = 'create_redirection_map.html'

# methods
def get_org_id(request):
    fer = Fernet(bytes(request.session["fk"],'utf-8'))
    decr_id = int(fer.decrypt(bytes(request.session["sk"],'utf-8')).decode())
    return decr_id

def get_user(id):
    user = models.Org.objects.filter(id=id).values()
    return user[0] 

def get_redirection_rules(id):
    redirection_rules = models.RedirectMap.objects.filter(org_id=id).values()
    return redirection_rules 

def gen_rand_str(size):
    randcode = ''.join(random.choices(randcode_string, k=size))
    return str(randcode)