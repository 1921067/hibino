from django import urls
from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
  path('',views.Login,name='Login'),
  path("logout",views.Logout,name="Logout"),
  path('register',views.AccountRegistration.as_view(), name='register'),
  path("index",views.index,name="index"),
  path("index<int:page>" ,views.index,name="index" ),
  path('groups', views.groups, name='groups'),
  path('add', views.add, name='add'),
  path('creategroup', views.creategroup, name='creategroup'),
  path('post', views.post, name='post'),
  path('share/<int:share_id>', views.share, name='share'),
  path('good/<int:good_id>', views.good, name='good'),
  path('post_list', views.News, name='News'),
]