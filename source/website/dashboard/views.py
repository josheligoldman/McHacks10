from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .forms import AddClassForm


def index(request):
    template = loader.get_template('dashboard/index.html')
    return HttpResponse(template.render({}, request))


def get_class(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddClassForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(cleaned_data)
            return HttpResponseRedirect('')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddClassForm()

    return render(request, 'dashboard/index.html', {'form': form})

