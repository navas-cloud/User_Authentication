from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ForgotPasswordForm,
    ProfileForm,
    FileUploadForm,
    FileCategoryMappingForm
)
from .models import File, Category, Profile, CustomUser, FileCategoryMapping, FileAccess, ActivityLog
from .decorator import role_required  
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .utils import generate_email_otp, get_daily_passcode
from django.http import JsonResponse
from .models import UploadedFile, Category
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta

User = get_user_model()

def log_activity(user, action):
    ActivityLog.objects.create(
        user=user if user.is_authenticated else None,
        role=user.role if user.is_authenticated else "Anonymous",
        action=action
    )

def register_page(request):
    form = CustomUserCreationForm()
    context = {
        'form': form,
        'email': request.session.get('email_to_verify', ''),
        'otp_sent': request.session.get('otp_sent', False),
        'email_verified': request.session.get('email_verified', False),
    }
    return render(request, 'register.html', context)

@require_POST
def send_otp(request):
    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required'})

    otp = generate_email_otp()
    request.session['email_otp'] = otp
    request.session['email_to_verify'] = email
    request.session['otp_sent'] = True
    request.session['email_verified'] = False

    send_mail(
        'Your OTP Verification Code',
        f'Your OTP is {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

    return JsonResponse({'status': 'success', 'message': f'OTP sent to {email}'})

@require_POST
def verify_otp(request):
    otp_input = request.POST.get('otp_input', '').strip()
    session_otp = request.session.get('email_otp', '')

    if otp_input == session_otp:
        request.session['email_verified'] = True
        return JsonResponse({'status': 'success', 'message': 'Email verified successfully!'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})

@require_POST
def register_submit(request):
    email_verified = request.session.get('email_verified', False)
    form = CustomUserCreationForm(request.POST)

    if not email_verified:
        return JsonResponse({'status': 'error', 'errors': {'email': ['Email must be verified']}})

    if form.is_valid():
        role = form.cleaned_data.get('role')
        passcode = form.cleaned_data.get('passcode')

        if role in ['admin', 'manager'] and passcode != get_daily_passcode():
            return JsonResponse({'status': 'error', 'errors': {'passcode': ['Invalid passcode for selected role']}})

        user = form.save()
        login(request, user)
        log_activity(user, f"Registered new user with role: {user.role}")

        for key in ['email_verified', 'email_otp', 'email_to_verify', 'otp_sent']:
            request.session.pop(key, None)

        return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})

    else:
        return JsonResponse({'status': 'error', 'errors': form.errors})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_activity(user, "Logged in")
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, "login.html", {'form': form})

User = get_user_model()

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']

            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                log_activity(user, "Password reset")
                messages.success(request, "Password reset successful! Please log in with your new password.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


User = get_user_model()

@login_required
def dashboard(request):
    recent_files = UploadedFile.objects.order_by('-uploaded_at')[:5]
    total_files = UploadedFile.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    
    context = {
        "recent_files": recent_files,
        "total_files": total_files,
        "total_categories": total_categories,
        "total_users": total_users,
    }
    return render(request, "dashboard.html", context)

@login_required
def chart_data(request):
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    upload_counts = [UploadedFile.objects.filter(uploaded_at__date=d).count() for d in dates]
    upload_dates = [d.strftime("%b %d") for d in dates]

    categories = Category.objects.annotate(count=Count('files'))
    category_names = [c.name for c in categories]
    category_counts = [c.count for c in categories]

    return JsonResponse({
        "upload_dates": upload_dates,
        "upload_counts": upload_counts,
        "category_names": category_names,
        "category_counts": category_counts
    })

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    current_date = timezone.now().strftime('%a, %d %B %Y')

    context = {
        'profile': profile,
        'current_date': current_date
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Updated profile")
            return redirect('profile') 
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
@role_required(['employee', 'manager', 'admin'])
def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploader = request.user
            file.save()
            log_activity(request.user, f"Uploaded file: {file.title}")
            messages.success(request, "File uploaded successfully!")
            return redirect('file_upload')
    else:
        form = FileUploadForm()

    if request.user.role == 'admin':
        file_list = File.objects.all().order_by('-uploaded_at')
    elif request.user.role == 'manager':
        file_list = File.objects.filter(uploader__role='employee').order_by('-uploaded_at')
    else:
        file_list = File.objects.filter(uploader=request.user).order_by('-uploaded_at')

    paginator = Paginator(file_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'form': form, 'page_obj': page_obj}
    return render(request, 'file_upload.html', context)

@login_required
@role_required(['manager', 'admin'])
def file_edit_view(request, file_id):
    file = get_object_or_404(File, id=file_id)
    form = FileUploadForm(request.POST or None, request.FILES or None, instance=file)

    if request.method == 'POST':
        if form.is_valid():
            file = form.save(commit=False)
            file.updated_by = request.user
            file.save()
            log_activity(request.user, f"Edited file: {file.title}")
            messages.success(request, "File updated successfully!")
            return redirect('file_upload')

    return render(request, 'file_edit.html', {'form': form, 'file': file})

@login_required
@role_required(['manager', 'admin'])
def file_delete_view(request, file_id):
    try:
        file = File.objects.get(id=file_id)
        file_title = file.title
        file.delete()
        log_activity(request.user, f"Deleted file: {file_title}")
        messages.success(request, "File deleted successfully!")
    except File.DoesNotExist:
        messages.error(request, "File not found.")
    return redirect('file_upload')

@login_required
@role_required(['admin', 'manager'])
def category_list_view(request):
    categories = Category.objects.all().order_by('name')
    assignments = FileCategoryMapping.objects.select_related('file', 'category', 'assigned_by').order_by('-assigned_at')
    users = CustomUser.objects.filter(role='employee').order_by('username')  # 👈 Add this line

    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')

        if assignment_id:
            mapping = get_object_or_404(FileCategoryMapping, id=assignment_id)
            new_category_id = request.POST.get('category')
            new_assign_to_ids = request.POST.getlist('assign_to')

            if new_category_id and str(mapping.category.id) != new_category_id:
                mapping.category_id = new_category_id

            if new_assign_to_ids:
                FileAccess.objects.filter(file=mapping.file).delete()
                for uid in new_assign_to_ids:
                    FileAccess.objects.update_or_create(
                        file=mapping.file,
                        user_id=uid,
                        defaults={'can_view': True, 'can_edit': False}
                    )

            mapping.reassigned_by = request.user
            mapping.reassigned_at = timezone.now()
            mapping.save()

            messages.success(request, "Reassignment updated successfully.")
            return redirect('category_list')

        else:
            form = FileCategoryMappingForm(request.POST)
            if form.is_valid():
                mapping = form.save(commit=False)
                mapping.assigned_by = request.user
                mapping.save()

                assigned_users = form.cleaned_data.get('assign_to')
                if assigned_users:
                    if not hasattr(assigned_users, '__iter__'):
                        assigned_users = [assigned_users]
                    for user in assigned_users:
                        FileAccess.objects.update_or_create(
                            file=mapping.file,
                            user=user,
                            defaults={'can_view': True, 'can_edit': False}
                        )

                messages.success(request, "File successfully assigned to category and users!")
                return redirect('category_list')
    else:
        form = FileCategoryMappingForm()

    context = {
        'categories': categories,
        'assignments': assignments,
        'form': form,
        'users': users,
    }
    return render(request, 'category_list.html', context)

@login_required
@role_required(['admin', 'manager'])
def delete_assignment_view(request, assignment_id):
    assignment = get_object_or_404(FileCategoryMapping, id=assignment_id)
    log_activity(request.user, f"Deleted assignment of file '{assignment.file.title}' to category '{assignment.category.name}'")
    assignment.delete()
    messages.success(request, f"Assignment of '{assignment.file.title}' to '{assignment.category.name}' deleted successfully.")
    return redirect('category_list')

@login_required
@role_required(['admin', 'manager'])
def user_list_view(request):
    users = CustomUser.objects.all().order_by('username')

    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)

    context = {
        'page_obj': page_obj,
        'now': now,
        'seven_days_ago': seven_days_ago, 
    }

    return render(request, 'user_list.html', context)

@login_required
@role_required(['admin'])
def delete_user_view(request, user_id):
    user_to_delete = get_object_or_404(CustomUser, id=user_id)

    if user_to_delete == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('user_list')
    log_activity(request.user, f"Deleted user: {user_to_delete.username}")
    user_to_delete.delete()
    messages.success(request, f"User {user_to_delete.username} has been deleted.")
    return redirect('user_list')

@login_required
@role_required(['admin'])
def activity_log_view(request):

    logs = ActivityLog.objects.all().order_by('-created_at') 

    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'activity_log.html', context)

def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request.user, "Logged out")
    logout(request)
    return redirect('login')
