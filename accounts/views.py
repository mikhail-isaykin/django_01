from django.urls import reverse_lazy
from django.views import generic
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib import messages


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    initial = None  # принимает {'key': 'value'}
    template_name = 'registration/signup.html'


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to='blog:post_list')
        return super(SignUpView, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})
