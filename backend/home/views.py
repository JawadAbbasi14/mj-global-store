from django.shortcuts import render

def home(request):
    return render(request,"home/home.html")

def about(request):
    return render(request,"home/about.html")

def contact(request):
    return render(request,"home/contact.html")

def privecy_and_policy(request):
    return render(request,"home/privecy_and_policy.html")

def terms_and_contitions(request):
    return render(request,"home/terms_and_contitions.html")
