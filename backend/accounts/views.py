from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Well come to MJ_GLOBAL_STORE home page !")


from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Home Page")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        feedback = request.POST['feedback']

        print("User input:", username, password, email)
        return HttpResponse("Signup successfully jawad!")

    return render(request, "accounts/signup.html")

