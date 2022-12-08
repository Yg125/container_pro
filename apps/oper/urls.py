from django.urls import path
from . import views
urlpatterns = [
    path('select/', views.SelectCourse.as_view()),
    path('selectcourses/', views.ShowCourse.as_view()),
    path('selectedcourses/', views.SelectedCourse.as_view()),
    path('createcontainer/', views.CreateContainer.as_view()),
    path('stopcontainer/', views.StopContainer.as_view()),
    path('startcontainer/', views.StartContainer.as_view()),


]