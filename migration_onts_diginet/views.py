from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'migration_diginet_home.html')