from django.shortcuts import render

# Create your views here.
def home(request):
    """Render HTML index page"""
    return render(request, 'index.html')
