import json
from django.shortcuts import render
from django.http import HttpResponse
from maintenance_manager.static.shared_staticfiles.common.utils import GeneralUtility


def homepage(request):
    return render(request, 'homepage.html')

def check_file_names(request):
    if request.method == 'GET':
        file_names = GeneralUtility.check_file_names(request)

        return HttpResponse(json.dumps(file_names))
