from django.urls import path

from . import views

urlpatterns = [
    path('makefolder/', views.make_folder),
    path('searchfolder/', views.search_folder),
    path('makefile/', views.make_file),
    path('searchfile/', views.search_file),
    path('updatefile/', views.update_file),
]
