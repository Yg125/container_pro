from django.urls import path, re_path

from apps.lab import views

urlpatterns = [
    re_path(r'^courses/$', views.CoursesView.as_view({'get': 'list', "post": "create"})),
    re_path(r'^courses/(?P<pk>\d+)/$',
            views.CoursesView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    re_path(r'^images/$', views.ImagesView.as_view({'get': 'list', "post": "create"})),
    re_path(r'^images/(?P<pk>\d+)/$',
            views.ImagesView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    re_path(r'^containers/$', views.ContainersView.as_view({'get': 'list', "post": "create"})),
    re_path(r'^containers/(?P<pk>\d+)/$',
            views.ContainersView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),  # 管理员查看某课程的容器内容
    re_path(r'^total/containers/$', views.TotalContainers.as_view()),
    re_path(r'^show/containers/$', views.ShowContainers.as_view()),  # 学生/老师查看某课程的容器内容
]
