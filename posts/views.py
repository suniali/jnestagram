from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth import logout

class HomeView(View):
    template_name = 'posts/home.html'

    def get(self, request):
        title='Welcome To Jnestagram Mate!'
        return render(request, self.template_name, {'title': title})
