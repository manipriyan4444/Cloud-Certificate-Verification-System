from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserLoginForm, StudentForm
from .models import Student

def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Allow login using username or student register_number
            user = authenticate(username=username, password=password)
            if not user:
                try:
                    student = Student.objects.get(register_number=username)
                    user = authenticate(username=student.user.username, password=password)
                except Student.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid username/register number or password.")
        else:
            # Check register number authentication if username was not matched directly by AuthenticationForm
            raw_username = request.POST.get('username')
            raw_password = request.POST.get('password')
            user = None
            try:
                student = Student.objects.get(register_number=raw_username)
                user = authenticate(username=student.user.username, password=raw_password)
            except Student.DoesNotExist:
                pass

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid username/register number or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    student = None
    if hasattr(user, 'student_profile'):
        student = user.student_profile

    return render(request, 'accounts/profile.html', {
        'user': user,
        'student': student
    })
