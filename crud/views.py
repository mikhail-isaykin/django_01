from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import Person
from .forms import PersonForm
from django.forms.models import model_to_dict


def index(request):
    form = PersonForm()
    people = Person.objects.all()
    return render(request, 'index.html', {'form': form, 'people': people})


def create(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = Person()
            person.name = form.cleaned_data['name']
            person.age = form.cleaned_data['age']
            person.save()
    return HttpResponseRedirect('/')


def edit(request, id):
    try:
        person = Person.objects.get(id=id)
    except Person.DoesNotExist:
        return HttpResponseNotFound('<h2>Person not found</h2>')

    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person.name = form.cleaned_data['name']
            person.age = form.cleaned_data['age']
            person.save()
        return HttpResponseRedirect('/')
    else:
        form = PersonForm(model_to_dict(person))
        return render(request, 'edit.html', {'form': form})


def delete(request, id):
    try:
        person = Person.objects.get(id=id)
    except Person.DoesNotExist:
        return HttpResponseNotFound('<h2>Person not found</h2>')

    person.delete()
    return HttpResponseRedirect('/')
