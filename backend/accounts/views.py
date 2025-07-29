from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


# function for home page :
def home(request):
    return render(request,'accounts/home.html')

# function for signup page:

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Empty checks
        if not username or not email or not password:
            messages.error(request, "Please fills all fields!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if password != confirm_password:
            messages.error(request, "Passwords does not match!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if len(password) < 8:
            messages.error(request, "Password must be 8 characters!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Check duplicates
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email pehlay se register hai!")
            return render(request, 'accounts/signup.html', {'username': username, 'email': email})

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Signup successful! Now login please.")
        return redirect('home')  # Redirect to the home page

    return render(request, 'accounts/signup.html')
