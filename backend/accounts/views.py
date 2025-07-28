from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")   
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Signup successful!")
                return redirect('home')  # ya login page
        else:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

    return render(request, 'signup.html')
