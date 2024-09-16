from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

import requests
from django.conf import settings

from django.urls import reverse_lazy
from .models import mold


class TopView(LoginRequiredMixin,ListView):
    model = mold
    context_object_name = "memos"

    def get_context_data(self,**kwargs):
       context = super().get_context_data(**kwargs)
       context["memos"] = context["memos"].filter(user=self.request.user) 
       searchInputText = self.request.GET.get("search") or ""
       if searchInputText:
           context["memos"] = context["memos"].filter(name__icontains=searchInputText)
        
       context["search"] = searchInputText
       
       return context
    

class DetailPage(LoginRequiredMixin,DetailView):
    model = mold
    context_object_name = "memo"

class CreatePage(LoginRequiredMixin,CreateView):
    model = mold
    fields = ["name","description","image","completed"]
    success_url = reverse_lazy("top")

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UpdatePage(LoginRequiredMixin,UpdateView):
    model = mold
    fields = "__all__"
    success_url = reverse_lazy("top")

class DeletePage(LoginRequiredMixin,DeleteView):
    model = mold
    fields = "__all__"
    success_url = reverse_lazy("top")

class LoginPage(LoginView):
    fields = "__all__"
    template_name = "foodmemoapp/login.html"

    def get_success_url(self):
        return reverse_lazy("top")
    
class RegisterPage(FormView):
    template_name = "foodmemoapp/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("top")

    def form_valid(self,form):
        user = form.save()
        if user is not None:
            login(self.request,user)
        return super().form_valid(form)


from requests.exceptions import RequestException
   
def search_restaurants(request):
    query = request.GET.get('query', "")
    places_data = []

    if query:
        url = 'https://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': settings.HOTPEPPER_API_KEY,
            'keyword': query,
            'format': 'json',
            'count': 5,
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                places_data = data.get('results', {}).get('shop', [])
            else:
                print(f"APIリクエストが失敗しました: {response.status_code}")
        except RequestException as e:
            print(f"APIリクエスト中にエラーが発生しました: {e}")
    
    return render(request, 'foodmemoapp/mold_form.html', {
        'query': query,
        'restaurants': places_data,  
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })
    
class TimelineView(LoginRequiredMixin, ListView):
    model = mold
    context_object_name = 'memos'
    template_name = 'foodmemoapp/timeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memos = mold.objects.exclude(user=self.request.user).order_by('-Date')
        for memo in memos:
            content = memo.description or memo.name
            memo.twitter_share_url = generate_twitter_share_url(content)

        context["memos"] = memos
        return context
    
from urllib.parse import quote
from django.shortcuts import get_object_or_404, redirect
from .models import mold


def generate_twitter_share_url(content, url=None):
    base_url = "https://twitter.com/intent/tweet"
    share_text = f"text={quote(content)}"
    if url:
        return f"{base_url}?{share_text}&url={quote(url)}"
    else:
        return f"{base_url}?{share_text}"


def share_on_twitter_view(request, pk):
    memo = get_object_or_404(mold, pk=pk)
    content = memo.description or memo.name
    url = request.build_absolute_uri(memo.get_absolute_url())
    twitter_share_url = generate_twitter_share_url(content, url)
    
    return redirect(twitter_share_url) 

