# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response

def user_login(request):
    if request.method == 'POST':
        pass
    else:
        render_to_response('login.html')