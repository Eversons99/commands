from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home_temp.html')

def render_onts_unauthorized(request):
    return render(request, 'onts_unauthorized.html')
