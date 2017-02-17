from django.shortcuts import render
from models import User, UserForm


# Create your views here.

def index(request):
    userinfo = User.objects.all()
    return render(request, 'HelloWorld.html', {'userinfo': userinfo})


def add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            post = form.save()

    userinfo = User.objects.all()
    return render(request, 'HelloWorld.html', {'userinfo': userinfo})
