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
    fields = ["name","description","image","completed"]
    success_url = reverse_lazy("top")
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)

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
from .forms import MoldForm
   
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def search_restaurants(request):
    query = request.GET.get('query', "")
    places_data = []
    form = MoldForm()  # フォームをレンダリング

    # 1ページあたりの店舗数
    per_page = 5

    if query:
        url = 'https://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': settings.HOTPEPPER_API_KEY,
            'keyword': query,
            'format': 'json',
            'count': 100,  # 最大数まで取得する（APIの制限内）
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

    # ページネーションの設定
    paginator = Paginator(places_data, per_page)
    page = request.GET.get('page')  # クエリパラメータからページ番号を取得

    try:
        restaurants = paginator.page(page)
    except PageNotAnInteger:
        restaurants = paginator.page(1)  # ページ番号が整数でない場合は最初のページ
    except EmptyPage:
        restaurants = paginator.page(paginator.num_pages)  # 存在しないページの場合は最後のページ

    return render(request, 'foodmemoapp/mold_form.html', {
        'form': form,
        'query': query,
        'restaurants': restaurants,  # ページネートされた店舗データ
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'paginator': paginator,
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
            url = self.request.build_absolute_uri(memo.get_absolute_url())
            memo.twitter_share_url = generate_twitter_share_url(content, url)

        context["memos"] = memos
        return context

    
from urllib.parse import quote
from django.shortcuts import get_object_or_404, redirect
from .models import mold
from urllib.parse import quote_from_bytes

def generate_twitter_share_url(content, url=None):
    base_url = "https://twitter.com/intent/tweet"
    
    # contentがNoneの場合は空文字に置き換え
    if content is None:
        content = ""

    share_text = f"text={quote_from_bytes(content.encode('utf-8'))}"

    # urlがNoneの場合の処理
    if url:
        return f"{base_url}?{share_text}&url={quote_from_bytes(url.encode('utf-8'))}"
    else:
        return f"{base_url}?{share_text}"


def share_on_twitter_view(request, pk):
    memo = get_object_or_404(mold, pk=pk)
    content = memo.description or memo.name
    url = request.build_absolute_uri(memo.get_absolute_url())
    twitter_share_url = generate_twitter_share_url(content, url)
    print(f"Generated Twitter URL: {twitter_share_url}")
    return redirect(twitter_share_url) 


from django.shortcuts import render, redirect
from .models import ImageModel
from .forms import ImageForm  # フォームを定義

def create_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            # ユーザーが回転ボタンを押したかどうかで回転フラグを設定
            image_instance.is_rotated = request.POST.get('rotate') == 'on'
            image_instance.save()
            return redirect('image_list')
    else:
        form = ImageForm()
    
    return render(request, 'create_image.html', {'form': form})
