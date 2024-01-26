from django.urls import path, register_converter
from . import views
from .converters import IntListConverter
from django.urls import path, include
from django.contrib.auth import views as auth_views

#Using Django path converter to take in list in the parameters. This is required because the rows in the planning duty feature groups together data that have the same starting and ending time.
register_converter(IntListConverter, 'int_list')

urlpatterns = [
    path('', views.index, name='index'),
    path('trooper_duty_chart', views.trooper_duty_chart, name='trooper_duty_chart'),
    path('daily_leaves_chart', views.daily_leaves_chart, name='daily_leaves_chart'),
    path('most_leaves_chart', views.most_leaves_chart, name='most_leaves_chart'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    
    path('register/', views.register, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='reset_password'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='reset_password_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset.html'), name="rest_password_confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),

    path('trooper/manage_trooper/', views.manage_trooper, name='manage_trooper'),
    path('trooper/update_trooper/<int:trooper_id>/', views.update_trooper, name='update_trooper'),
    
    path('trooper/delete_trooper/<int:trooper_id>/', views.delete_trooper, name='delete_trooper'),
    path('trooper/manage_leave_type/', views.manage_leave_type, name='manage_leave_type'),
    path('trooper/delete_leave_type/<int:leave_type_id>/', views.delete_leave_type, name='delete_leave_type'),
    path('trooper/manage_leave/', views.manage_leave, name='manage_leave'),
    path('trooper/update_current_leave/<int:current_leave_id>/', views.update_current_leave, name='update_current_leave'),

    path('trooper/delete_current_leave/<int:current_leave_id>/', views.delete_current_leave, name='delete_current_leave'),
    path('trooper/load_leaves/', views.load_leaves, name='load_leaves'), # AJAX

    path('trooper/apply_leave/', views.apply_leave, name='apply_leave'),
    path('trooper/delete_apply_leave/<int:apply_leave_id>/', views.delete_apply_leave, name='delete_apply_leave'),
    path('trooper/update_apply_leave/<int:apply_leave_id>/', views.update_apply_leave, name='update_apply_leave'),

    path('duty/create_main_duty/', views.create_main_duty, name='create_main_duty'),
    path('duty/delete_main_duty/<int:main_duty_id>/', views.delete_main_duty, name='delete_main_duty'),
    path('duty/delete_multiple_main_duties/', views.delete_multiple_main_duties, name='delete_multiple_main_duties'),

    path('duty/create_additional_duty/', views.create_additional_duty, name='create_additional_duty'),
    path('duty/delete_additional_duty/<int:additional_duty_id>/', views.delete_additional_duty, name='delete_additional_duty'),

    path('duty/select_duty/', views.select_duty, name='select_duty'),
    path('duty/plan_duty/', views.plan_duty, name='plan_duty'),
    path('duty/add_main_duty/', views.add_main_duty, name='add_main_duty'),
    path('duty/add_additional_duty/', views.add_additional_duty, name='add_additional_duty'),

    path('duty/delete_trooper_main_duty/<int_list:duty_ids>/', views.delete_trooper_main_duty, name='delete_trooper_main_duty'),
    path('duty/delete_trooper_additional_duty/<int:duty_id>/', views.delete_trooper_additional_duty, name='delete_trooper_additional_duty'),
    
]