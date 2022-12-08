from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token

from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# router.register('info', )
urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('authorizations/', obtain_jwt_token),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('info/', views.UserInfoView.as_view()),
    path('roles/', views.RolesAPIView.as_view()),
    path('stu/total_count/', views.StuTotalNumber.as_view()),
    path('tea/total_count/', views.TeaTotalNumber.as_view()),
    path('sup/total_count/', views.SupTotalNumber.as_view()),
    path('day_increment/', views.UserDayIncrement.as_view()),
    path('month_increment/', views.UserMonthIncrement.as_view()),
    re_path(r'^users/$', views.UserView.as_view({'get': 'list', "post": "create"})),
    re_path(r'^users/(?P<pk>\d+)/$',
            views.UserView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]
