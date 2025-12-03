from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for analytics endpoints.
    
    - Default: 100 items per page
    - Client can request up to 1000 items via page_size parameter
    - Supports large result sets without memory issues
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
