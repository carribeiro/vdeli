# Create your views here.
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, RequestContext
from django.core import serializers

from forms import MainForm

def user_login(request):
    if request.method == 'POST':
        pass
    else:
        render_to_response('login.html')

def grid_handler(request):
    # handles pagination, sorting and searching
    from videorepo.grids import ProjectGrid
    grid = ProjectGrid()
    return HttpResponse(grid.get_json(request), mimetype="application/json")

def grid_config(request):
    # build a config suitable to pass to jqgrid constructor   
    from videorepo.grids import ProjectGrid
    grid = ProjectGrid()
    return HttpResponse(grid.get_config(), mimetype="application/json")

def ftpauth(request, username, password):
    """
    Simple JSON interface to test the user/password combination. To be used 
    with the FTP server. Note that passwords are sent in the clear, but that's
    also true for plain FTP.
    """
    from django.contrib.auth import authenticate
    import simplejson as json
    if True or ('application/json' in request.META.get('HTTP_ACCEPT')): # will ignore the header for now
        user = authenticate(username=username, password=password)
        if user:
            return HttpResponse(json.dumps({'status':'ok', 'username':user.username, }),
                    mimetype='application/json')
        else:
            return HttpResponseBadRequest(json.dumps({'status':'User/password combination do not match', 
                    'username':'', }), mimetype='application/json')
    else:
        return HttpResponseBadRequest(json.dumps({'status':'Must be called as a JSON method', 
                'username':'', }), mimetype='application/json')

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
    }, context_instance=RequestContext(request))

