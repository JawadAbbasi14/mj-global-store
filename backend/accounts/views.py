from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
import re

def home(request):
    return render(request, 'accounts/home.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Empty checks
        if not (username and email and password and confirm_password):
            messages.error(request, "Please fill all fields!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Password strength check
        if len(password) < 8 or not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            messages.error(request, "Password can't full fill our requriment!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Check duplicates
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Signup successful! Please log in.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Empty checks
        if not username or not password:
            messages.error(request, "Please provide both username and password!")
            return render(request, "accounts/login.html")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
            return render(request, "accounts/login.html")

    return render(request, "accounts/login.html")

# logout logic function

def logout_view(request):
    logout(request)
    return redirect("login_view")

