from django.shortcuts import render


def index(request):
    return render(request, 'blog/index.html', context={'site': 'Stepik.org'})


def about(request):
    return render(request, 'blog/about.html', context={'site': 'Stepik'})