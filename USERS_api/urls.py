# USERS_api/urls.py

from django.urls import path
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import UserRegisterView,UserDetailView,UserDeleteView,UserALLDelete, StockDataListCreate,StockDataDetail, TransactionCreate,UserTransactions

schema_view = get_schema_view(
   openapi.Info(
      title="API",
      default_version='v1',
      description="Test",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('users/', UserRegisterView.as_view(), name='user-list-create'),  # User List/Create
    path('users/<str:username>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<str:username>/delete/',UserDeleteView.as_view(),name='user_Delete'),
    path('users/delete/',UserALLDelete.as_view(),name='user_all_delete'),
    path('stockdata/', StockDataListCreate.as_view(), name='stockdata-list-create'),  # Stock Data List/Create
    path('stocks/<str:ticker>/', StockDataDetail.as_view(), name='stock-detail'),
    path('transactions/', TransactionCreate.as_view(), name='transactions-list-create'),  #    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('transactions/<str:username>/', UserTransactions.as_view(), name='user-transactions'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
