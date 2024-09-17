from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    page_size = 10  # Set default to 10
    page_size_query_param = 'page_size'  # Allow clients to adjust page size (optional)
    max_page_size = 100  # Maximum page size limit