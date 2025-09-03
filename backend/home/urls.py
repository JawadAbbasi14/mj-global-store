from django.urls import path
from . import views

urlpatterns = [

      path("",views.home,name="home"),
       path("about/",views.about,name="about"),
       path("contact/",views.contact,name="contact"),
       path("polices/",views.privecy_and_policy,name="policies"),
       path("contitions/",views.terms_and_contitions,name="terms"),
       path("help/",views.help,name="help"),

]
