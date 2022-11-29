from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    path('roles/', views.RolesAPIView.as_view()),
    path('authorizations/', obtain_jwt_token),
    path('stu/total_count/', views.StuTotalNumber.as_view()),
    path('tea/total_count/', views.TeaTotalNumber.as_view()),
    path('sup/total_count/', views.SupTotalNumber.as_view()),
    path('day_increment/', views.UserDayIncrement.as_view()),
    path('month_increment/', views.UserMonthIncrement.as_view()),
    re_path(r'^users/$', views.UserView.as_view({'get': 'list', "post": "create"})),
    re_path(r'^users/(?P<pk>\d+)/$',
            views.UserView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]
