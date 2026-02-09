from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import Person


# Получение данных из БД
def index(request):
    people = Person.objects.all()
    return render(request, 'index.html', {'people': people})


# Сохранение данных в БД
def create(request):
    if request.method == 'POST':
        person = Person()
        person.name = request.POST.get('name')
        person.age = request.POST.get('age')
        person.save()
    return HttpResponseRedirect('/')
