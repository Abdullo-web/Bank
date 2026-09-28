from django.urls import path
from .views import *
urlpatterns = [
    path('',Register.as_view(),name='register'),
    path('login/',Login.as_view(),name='login'),
    path('logout/',Logout.as_view(),name='logout'),
    path('account_create/',AccountCreate.as_view(),name='account_create'),
    path('account/', AccountDetail.as_view(), name='account'),
    path('card_create/', CardCreate.as_view(), name='card_create'),
    path('card_detail/<int:pk>/', CardDetail.as_view(), name='card_detail'),
    path('transfer/', transfer_view, name='transfer'),
    path('history/', transaction_history_view, name='history'),
    path('card/<int:card_id>/history/', transaction_history_view, name='card_history')
]