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


    #User
    path('otp/', OTPGenerationView.as_view(), name='otp-generation'),
    path('otp/verify/', OTPVerificationView.as_view(), name='otp-verification'),

    #Variant
    path('variant-types/', VariantTypeCreateListView.as_view(), name='variant-type-list-create'),
    path('variant-options/', VariantOptionCreateListView.as_view(), name='variant-option-list-create'),


    #Ckecking
    path('check-token/', CheckTokenView.as_view(), name='check_token'),


]


