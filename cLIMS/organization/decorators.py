'''
Created on Dec 5, 2016

@author: nanda
'''
from django.contrib.auth import get_user
from cLIMS import settings
from django.shortcuts import redirect
from django.views.generic.base import View
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from organization.models import Project
 
 
# content_type = ContentType.objects.get_for_model(User)
# permission = Permission.objects.create(
#     codename='view_only_user',
#     name='Can only view', 
#     content_type=content_type,
# ) 

def require_permission(view):
    def new_view(request, *args, **kwargs):
        userID = get_user(request).id
        ownerID = request.session['project_ownerId']
        ownertype=request.session['currentGroup']
        prjID = request.session['project_id']
        mem = Project.objects.get(pk=prjID).project_contributor.values_list('id', flat=True)
        if (ownertype == "admin"):
            return view(request, *args, **kwargs)
        elif(ownerID==userID or userID in mem):
            return view(request, *args, **kwargs)
        else:
            url = '{}?next={}'.format(
                settings.Error_URL,
                request.path)
            return redirect(url)
    return new_view


def class_login_required(cls):
    #print("Class: ",cls)
    if (not isinstance(cls, type) or not issubclass(cls, View)):
        raise ImproperlyConfigured("class_login_required must be applied to subclass of View class.")
    decorator = method_decorator(login_required)
    cls.dispatch = decorator(cls.dispatch)
    return cls

def view_only(view):
    def new_view(request, *args, **kwargs):
        view_only = request.session['view_only_user']
        if (view_only == True):
            url = '{}?next={}'.format(
                settings.Error_URL_view,
                request.path)
            return redirect(url)
        else:
            return view(request, *args, **kwargs)
    return new_view
    

