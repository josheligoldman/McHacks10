import sys

from django.shortcuts import render
from django.conf import settings

# Create your views here.

from django.http import HttpResponseRedirect
from django.template import loader

from .forms import AddClassForm

from scraper import scraper_testbench


def index_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddClassForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(request.POST)
            if "add_class" in request.POST:
                classes = request.session.get('classes', [])
                classes.append(form.cleaned_data['added_class'])
                request.session['classes'] = classes
                print("Classes", request.session.get('classes', []))
            elif "done" in request.POST:
                return HttpResponseRedirect('/build')
            else:
                classes = request.session.get('classes', [])
                for index in range(len(classes)):
                    if "delete_" + str(index) in request.POST:
                        classes = request.session.get('classes', [])
                        classes.pop(index)
                        request.session['classes'] = classes

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
    dataset = scraper_testbench.test_file_creation()

    del request.session['classes']

    context = {

    }

    return render(
        request,
        'dashboard/build.html',
        context,
    )


def build_dataset():
    return "/Users/joshgoldman/Documents/GitHub/McHacks10/datasets"

