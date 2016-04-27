from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'gaugeviewer/home.html', context)

def ahpsgauges(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'gaugeviewer/ahpsgauges.html', context)