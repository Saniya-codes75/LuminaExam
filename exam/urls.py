from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start-exam/<int:exam_id>/', views.start_exam, name='start_exam'),
    path('leaderboard/<int:exam_id>/', views.leaderboard, name='leaderboard'),
    path('profile/', views.profile, name='profile'),
    path('result/<int:exam_id>/', views.result_view, name='result'),
    path('instructions/<int:exam_id>/', views.exam_instructions, name='exam_instructions'),
    
    path('marksheet/<int:exam_id>/', views.generate_marksheet, name='generate_marksheet'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    
    path('home/', views.home_redirect, name='home_redirect'),
    path('view-results/<int:exam_id>/', views.admin_view_results, name='admin_view_results'),
    path('add-question/<int:exam_id>/', views.add_question, name='add_question'),
    
    path('exam-results/<int:exam_id>/', views.view_exam_results, name='view_exam_results'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
]