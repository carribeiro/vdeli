# Create your views here.
import os
import logging

from django.conf import settings
from django.core import serializers
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext, \
    get_object_or_404
from celery.execute import send_task

from forms import MainForm
from videorepo.forms import VideoProjectForm, ProjectPolicyFormSet, PolicyProjectForm
from videorepo.models import VideoProject
from django.core.urlresolvers import reverse

def user_login(request):
    if request.method == 'POST':
        pass
    else:
        render_to_response('login.html')

@login_required
def video_files_by_user_grid_handler(request):
    # handles pagination, sorting and searching
    from videorepo.grids import VideoFilesByUserGrid
    grid = VideoFilesByUserGrid(request.user)
    #import pdb; pdb.set_trace()
    return HttpResponse(grid.get_json(request), mimetype="application/json")

@login_required
def video_files_by_user_grid_config(request):
    # build a config suitable to pass to jqgrid constructor   
    from videorepo.grids import VideoFilesByUserGrid
    grid = VideoFilesByUserGrid(request.user)
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

@login_required
def main(request):
    kwargs = {'user': request.user}
    if request.method == 'POST':
        main_form = MainForm(request.POST, request.FILES, **kwargs)
        if main_form.is_valid():
            if main_form.cleaned_data['project_name'].name == 'default video project':
                video_project = 'default'
            else:
                video_project = main_form.cleaned_data['project_name'].name

            user_dir = '%s/%s' % (settings.MEDIA_ROOT, request.user)
            if not os.path.exists(user_dir):
                logging.debug("User directory does not exists: %s " % user_dir)
                os.mkdir(user_dir)
                os.chmod(user_dir, 0777) # TODO: improve this solution. see ticket #25

            user_project_dir = '%s/%s' % (user_dir, video_project)
            if not os.path.exists(user_project_dir):
                logging.debug("Project directory does not exists: %s " % user_project_dir)
                os.mkdir(user_project_dir)
                os.chdir(user_dir)
                os.chmod(video_project, 0777) # TODO: improve this solution. see ticket #25

            uploaded_file = '%s/%s' % (user_project_dir, \
                                       request.FILES['video_file'].name)

            destination = open(uploaded_file, 'wb+')
            for chunk in request.FILES['video_file'].chunks():
                destination.write(chunk)
            destination.close()

            try:
                result = send_task("videofile.import", [uploaded_file])
                print uploaded_file, result
            except:
                print "Failure on the call to celery.send_task"

            # Process the data in form.cleaned_data
            # ...
            # TODO: Just reload the current form. I've redirecting to 
            # itself, but there must be a more elegant way of doing it.
            return HttpResponseRedirect('')
    else:
        main_form = MainForm(**kwargs) # An unbound form

    return render_to_response('main_form.html', {
        'main_form': main_form,
    }, context_instance=RequestContext(request))

@login_required
def add_project(request, project_id=None):
    if project_id:
        vproject = get_object_or_404(VideoProject, pk=project_id)
    else:
        vproject = VideoProject()

    if request.method == 'POST':
        if vproject.name:
            form = VideoProjectForm(instance=vproject)
        else:
            form = VideoProjectForm(request.POST)

        if form.is_valid():
            video_project = form.save(commit=False)
            video_project.user = request.user
            policy_project_formset = ProjectPolicyFormSet(request.POST, instance=video_project)
            if policy_project_formset.is_valid():
                video_project.save()
                policy_project_formset.save()
            else:
                logging.debug('policy_project_form is invalid')
        else:
            logging.debug('video_project_form is invalid')

        return HttpResponseRedirect(reverse('main_page'))

    else:
        project_form = VideoProjectForm()
        policy_formset = ProjectPolicyFormSet(instance=vproject)

    return render_to_response('project_form.html',
                              {'project_form': project_form,
                               'policy_formset': policy_formset,
             }, context_instance=RequestContext(request))

@login_required
def transfer_queue(request):
    main_form = MainForm() # An unbound form
    return render_to_response('transfer_queue.html', {
        'main_form': main_form,
    }, context_instance=RequestContext(request))

@login_required
def transfer_queue_grid_handler(request):
    # handles pagination, sorting and searching
    from videorepo.grids import TransferQueueGrid
    grid = TransferQueueGrid(request.user)
    return HttpResponse(grid.get_json(request), mimetype="application/json")

@login_required
def transfer_queue_grid_config(request):
    # build a config suitable to pass to jqgrid constructor   
    from videorepo.grids import TransferQueueGrid
    grid = TransferQueueGrid(request.user)
    return HttpResponse(grid.get_config(), mimetype="application/json")

