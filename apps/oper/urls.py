from django.urls import path, re_path
from . import views

urlpatterns = [
    path('select/', views.SelectCourse.as_view()),
    path('selectcourses/', views.ShowCourse.as_view()),
    path('selectedcourses/', views.SelectedCourse.as_view()),
    path('createcontainer/', views.CreateContainer.as_view()),
    path('createservice/', views.CreateService.as_view()),
    path('stopcontainer/', views.StopContainer.as_view()),
    path('startcontainer/', views.StartContainer.as_view()),
    path('restartservice/', views.RestartService.as_view()),
    path('stopservice/', views.StopService.as_view()),
    path('removeservice/', views.RemoveService.as_view()),
    re_path(r'^courses/$', views.TeaCourses.as_view({'get': 'list', "post": "create"})),
    re_path(r'^courses/(?P<pk>\d+)/$',
            views.TeaCourses.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('files/', views.Files.as_view()),
    path('build/', views.Build.as_view()),
    path('commit/', views.CommitContainer.as_view()),
    path('update/', views.UpdateContainer.as_view()),
    path('server/', views.Server.as_view()),
]
