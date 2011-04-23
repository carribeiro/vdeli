# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response
from forms import MainForm

def user_login(request):
    if request.method == 'POST':
        pass
    else:
        render_to_response('login.html')

def main(request):
    if request.method == 'POST':
        main_form = MainForm(request.POST)
        if main_form.is_valid():
            # Process the data in form.cleaned_data
            # ...
            # TODO: Just reload the current form. I've redirecting to 
            # itself, but there must be a more elegant way of doing it.
            return HttpResponseRedirect('') 
    else:
        main_form = MainForm() # An unbound form

    return render_to_response('main_form.html', {
        'main_form': main_form,
    })