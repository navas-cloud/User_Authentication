from django.urls import path
from UserApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register_page, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('register-submit/', views.register_submit, name='register_submit'),
    path('', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/chart-data/', views.chart_data, name='chart_data'),    
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),    
    path('filesupload/', views.file_upload_view, name='file_upload'),
    path('files/edit/<int:file_id>/', views.file_edit_view, name='file_edit'),
    path('files/delete/<int:file_id>/', views.file_delete_view, name='file_delete'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/delete-assignment/<int:assignment_id>/', views.delete_assignment_view, name='delete_assignment'),
    path('user_list/', views.user_list_view, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
