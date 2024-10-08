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


    #Wishlist
    path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/add/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),

    #Cart
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/remove/<int:product_id>/<int:variant_id>/', RemoveFromCartView.as_view(), name='remove-from-cart-variant'),
    path('cart/update/<int:product_id>/', UpdateCartQuantityView.as_view(), name='update-cart-quantity'),
    path('cart/update/<int:product_id>/<int:variant_id>/', UpdateCartQuantityView.as_view(), name='update-cart-quantity-variant'),


    #Address
    path('addresses/', ListAddressesView.as_view(), name='list-addresses'),  # List all addresses
    path('addresses/create/', CreateAddressView.as_view(), name='create-address'),  # Create new address
    path('addresses/<int:pk>/edit/', UpdateAddressView.as_view(), name='edit-address'),  # Update address
    path('addresses/<int:pk>/delete/', DeleteAddressView.as_view(), name='delete-address'),  # Delete address

    #Order
    path('orders/buy-now/', BuyNowView.as_view(), name='buy-now'),  # Buy a single product
    path('orders/buy-all/', BuyAllFromCartView.as_view(), name='buy-all'),  # Buy all products in cart
    path('orders/', ListOrdersView.as_view(), name='list-orders'),  # List all orders
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),  # Order detail
    path('orders/<int:pk>/edit/', UpdateOrderView.as_view(), name='edit-order'),  # Update order
    path('orders/<int:pk>/delete/', DeleteOrderView.as_view(), name='delete-order'),  # Delete order
]


