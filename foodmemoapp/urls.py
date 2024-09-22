from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import TopView,DetailPage,CreatePage,UpdatePage,DeletePage,LoginPage,RegisterPage,TimelineView,share_on_twitter_view
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("",TopView.as_view(),name="top"),
    path('memo/<int:pk>/',DetailPage.as_view(),name="memo-detail"),
    path('create-memo/',CreatePage.as_view(),name='create-memo'),
    path('edit-memo/<int:pk>/',UpdatePage.as_view(),name='edit-memo'),
    path('delete-memo/<int:pk>/',DeletePage.as_view(),name='delete-memo'),
    path('login/',LoginPage.as_view(),name="login"),
    path('logout/',LogoutView.as_view(next_page="login"),name="logout"),
    path('register/',RegisterPage.as_view(),name="register"),
    path('search/', views.search_restaurants, name='search_restaurants'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
    path('memo/<int:pk>/share/twitter/', share_on_twitter_view, name='share_on_twitter'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)