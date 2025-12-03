from django.db.models import Q

def apply_dynamic_filters(queryset, params, exclude_keys=None):
    """
    Applies dynamic filters to a queryset based on request parameters.
    
    Args:
        queryset: Django QuerySet to filter
        params: Dictionary of filter parameters (e.g., request.query_params)
        exclude_keys: List of parameter keys to ignore
    
    Supported Filters:
        - Standard Django lookups: field__gte=value, field__icontains=value
        - NOT logic: not__field=value
        - OR logic: or__field1=value, or__field2=value (combined with OR)
        - Range: range=month/week/year (filters by timestamp or created_at)
    
    Examples:
        ?title__icontains=django
        ?not__status=archived
        ?or__category=tech&or__category=news
        ?range=month
    
    Returns:
        Filtered QuerySet
    """
    if exclude_keys is None:
        exclude_keys = []
    
    filters = Q()
    or_filters = Q()
    
    for key, value in params.items():
        if key in exclude_keys:
            continue
        
        if key.startswith('not__'):
            field = key.replace('not__', '', 1)
            filters &= ~Q(**{field: value})
        elif key.startswith('or__'):
            field = key.replace('or__', '', 1)
            or_filters |= Q(**{field: value})
        else:
            filters &= Q(**{key: value})
            
    if or_filters:
        filters &= or_filters

    if 'range' in params:
        range_val = params['range']
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        start_date = None
        
        if range_val == 'month':
            start_date = now - timedelta(days=30)
        elif range_val == 'week':
            start_date = now - timedelta(weeks=1)
        elif range_val == 'year':
            start_date = now - timedelta(days=365)
            
        if start_date:
            model = queryset.model
            date_field = None
            if hasattr(model, 'timestamp'):
                date_field = 'timestamp'
            elif hasattr(model, 'created_at'):
                date_field = 'created_at'
            
            if date_field:
                queryset = queryset.filter(**{f"{date_field}__gte": start_date})

    return queryset.filter(filters)
