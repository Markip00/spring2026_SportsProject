from django.urls import path
from . import views
 
 
urlpatterns = [
    path('', views.home, name='home'),
    path('scores/', views.scores, name='scores'),
    path("spaces/", views.spaces, name="spaces"),
    path('clips/' , views.clips , name = 'clips' ),
    path('edit_profile/' , views.edit_profile , name = 'edit_profile' ),
    path('add_friends/' , views.add_friends , name = 'add_friends' ),
    path('direct_messages/' , views.direct_messages , name = 'direct_messages' ),
    path('premium/' , views.premium , name = 'premium' ),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
 
 