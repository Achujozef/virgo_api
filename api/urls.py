from django.urls import path
from .views import *

urlpatterns = [
    #Category
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/list/', CategoryListView.as_view(), name='category-tree'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),


    #Product 
    path('products/detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/category/<int:category_id>/', ProductListByCategoryView.as_view(), name='product-by-category'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/all/', ProductListView.as_view(), name='products-list'),
]

