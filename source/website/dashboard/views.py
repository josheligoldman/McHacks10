import asyncio
import time

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .forms import AddClassForm


def index_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddClassForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if "add_class" in request.POST:
                classes = request.session.get('classes', [])
                classes.append(form.cleaned_data['added_class'])
                request.session['classes'] = classes
                print("Classes", request.session.get('classes', []))
            else:
                return HttpResponseRedirect('/build')

    context = {
        'form': AddClassForm(),
        'classes': request.session.get('classes', []),
    }

    return render(
        request,
        'dashboard/index.html',
        context
    )


def dataset_view(request):
    dataset = build_dataset()

    context = {

    }

    return render(
        request,
        'dashboard/build.html',
        context,
    )


def build_dataset():
    return 0

