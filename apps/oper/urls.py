from django.urls import path
from . import views
urlpatterns = [
    path('select/', views.SelectCourse.as_view()),
    path('showtocourses/', views.ShowCourse.as_view()),
    path('showcourses/', views.SelectedCourse.as_view()),
    path('container/', views.CreateContainer.as_view()),
]