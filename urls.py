from django.urls import path,include,re_path
from . import views

urlpatterns = [
    path('',views.start,name='start'),
    path('signup/',views.signup,name='signup'),
    path('signin/',views.signin,name='signin'),
    path('home/',views.home,name='home'),
    path('create_rl/',views.create_redirection_map,name='create_redirection_map'),
    path('delete_rl/<int:rl_id>',views.delete_redirection_map,name='delete_redirection_map'),
    path('edit_rl/<int:rl_id>',views.edit_redirection_map,name='edit_redirection_map'),
    path('signout/',views.signout,name='signout'),
    re_path(r'(?P<short_code>[A-Z]{3,4}-[a-zA-Z0-9]{5})',views.main_redirection,name='main_redirection')
]
