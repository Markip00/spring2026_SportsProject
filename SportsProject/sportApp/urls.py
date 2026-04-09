from django.urls import path
from . import views
 
 
urlpatterns = [
    path('', views.home, name='home'),
    path('news/', views.news, name='news'),
    path('watchparty/' , views.watchparty , name = 'watchparty' ),
    path('spaces/' , views.spaces , name = 'spaces' ),
    path('clips/' , views.clips , name = 'clips' ),
    path('edit_profile/' , views.edit_profile , name = 'edit_profile' ),
    path('add_friends/' , views.add_friends , name = 'add_friends' ),
    path('direct_messages/' , views.direct_messages , name = 'direct_messages' ),
    path('premium/' , views.premium , name = 'premium' ),
    path('sign_up/' , views.sign_up , name = 'sign_up' ),
    path('log_in/' , views.log_in , name = 'log_in' ),
]
 
 