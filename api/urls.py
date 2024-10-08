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

    #Offer
    path('offers/', OfferListView.as_view(), name='offer-list'),  # GET list of offers
    path('offers/create/', OfferCreateView.as_view(), name='offer-create'),  # POST create a new offer
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),  # GET retrieve an offer
    path('offers/<int:pk>/update/', OfferUpdateView.as_view(), name='offer-update'),  # PUT or PATCH update an offer
    path('offers/<int:pk>/delete/', OfferDeleteView.as_view(), name='offer-delete'),  # DELETE remove an offer


    #Coupen
    path('coupons/', CouponListView.as_view(), name='coupon-list'),
    path('coupons/create/', CouponCreateView.as_view(), name='coupon-create'),
    path('coupons/<int:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
    path('coupon-apply/', ApplyCouponView.as_view(), name='apply-coupon'),
    path('coupon-usage/', CouponUsageListView.as_view(), name='coupon-usage-list'),

    #Testmonials
    path('testimonials/', TestimonialListView.as_view(), name='testimonial-list'),  # List all testimonials
    path('testimonials/create/', TestimonialCreateView.as_view(), name='testimonial-create'),  # Create a testimonial
    path('testimonials/<int:pk>/', TestimonialDetailView.as_view(), name='testimonial-detail'),  # Retrieve a testimonial
    path('testimonials/<int:pk>/update/', TestimonialUpdateView.as_view(), name='testimonial-update'),  # Update a testimonial

    #Review
    path('reviews/create/', ReviewCreateView.as_view(), name='review-create'),  # Create a review
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),  # Retrieve a review
    path('reviews/<int:pk>/update/', ReviewUpdateView.as_view(), name='review-update'),  # Update a review
    path('products/<int:product_id>/reviews/', ProductReviewListView.as_view(), name='product-review-list'),  # List reviews for a product
    path('products/<int:product_id>/reviews/approved/', ProductReviewListViewApproved.as_view(), name='product-review-list-approved'),  # List approved reviews for a product

    #Order Message
    path('orders/<int:order_id>/messages/', OrderMessageListView.as_view(), name='order-message-list'),
    path('orders/<int:order_id>/messages/create/', OrderMessageCreateView.as_view(), name='order-message-create'),
]


