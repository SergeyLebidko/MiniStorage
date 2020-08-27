from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required


class Login(LoginView):
    template_name = 'main/login.html'


@login_required(login_url='login')
def index(request):
    return render(request, 'main/index.html', context={})
