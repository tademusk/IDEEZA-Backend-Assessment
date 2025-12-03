from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear, TruncDay
from .models import Blog, View, User, Country
from .utils import apply_dynamic_filters

class BlogViewsAnalytics(APIView):
    """
    Analytics API for blog views grouped by user or country.
    
    Query Parameters:
        - object_type (required): 'user' or 'country'
        - range (optional): 'month', 'week', or 'year'
        - Dynamic filters supported (e.g., user__name__icontains, not__field)
    
    Returns:
        List of {x: name, y: blog_count, z: view_count}
    """
    def get(self, request):
        object_type = request.query_params.get('object_type')
        queryset = Blog.objects.select_related('user', 'user__country').prefetch_related('views')
        
        range_val = request.query_params.get('range')
        view_filter = Q()
        if range_val:
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
                view_filter = Q(views__timestamp__gte=start_date)

        queryset = apply_dynamic_filters(queryset, request.query_params, exclude_keys=['object_type', 'range'])

        if object_type == 'user':
            data = queryset.values('user__name').annotate(
                x=F('user__name'),
                y=Count('id', distinct=True),
                z=Count('views', filter=view_filter, distinct=True)
            ).order_by('-z')
        elif object_type == 'country':
            data = queryset.values('user__country__name').annotate(
                x=F('user__country__name'),
                y=Count('id', distinct=True),
                z=Count('views', filter=view_filter, distinct=True)
            ).order_by('-z')
        else:
            return Response({"error": "Invalid object_type"}, status=400)

        return Response(list(data))

class TopAnalytics(APIView):
    """
    Returns Top 10 items based on total views.
    
    Query Parameters:
        - top (required): 'user', 'country', or 'blog'
        - Dynamic filters supported
    
    Returns:
        List of top 10 {x: name, y: views, z: additional_metric}
    """
    def get(self, request):
        top_type = request.query_params.get('top')
        
        if top_type == 'blog':
            queryset = Blog.objects.select_related('user').prefetch_related('views')
            queryset = apply_dynamic_filters(queryset, request.query_params, exclude_keys=['top'])
            data = queryset.annotate(
                x=F('title'),
                y=Count('views'),
                z=Count('views')
            ).order_by('-y')[:10]
        elif top_type == 'user':
            queryset = User.objects.select_related('country').prefetch_related('blogs', 'blogs__views')
            data = queryset.annotate(
                x=F('name'),
                y=Count('blogs__views'),
                z=Count('blogs', distinct=True)
            ).order_by('-y')[:10]
        elif top_type == 'country':
            queryset = Country.objects.prefetch_related('users', 'users__blogs', 'users__blogs__views')
            data = queryset.annotate(
                x=F('name'),
                y=Count('users__blogs__views'),
                z=Count('users', distinct=True)
            ).order_by('-y')[:10]
        else:
            return Response({"error": "Invalid top_type"}, status=400)
            
        return Response(list(data.values('x', 'y', 'z')))

class PerformanceAnalytics(APIView):
    """
    Time-series performance analytics with growth metrics.
    
    Query Parameters:
        - compare (required): 'month', 'week', 'day', or 'year'
        - Dynamic filters supported
    
    Returns:
        List of {x: period_label, y: views, z: growth_percentage}
    """
    def get(self, request):
        compare_period = request.query_params.get('compare')
        
        queryset = View.objects.select_related('blog', 'blog__user')
        queryset = apply_dynamic_filters(queryset, request.query_params, exclude_keys=['compare'])
        
        trunc_func = {
            'month': TruncMonth,
            'week': TruncWeek,
            'day': TruncDay,
            'year': TruncYear
        }.get(compare_period)
        
        if not trunc_func:
            return Response({"error": "Invalid compare period"}, status=400)
            
        data = queryset.annotate(
            period=trunc_func('timestamp')
        ).values('period').annotate(
            y=Count('id'),
        ).order_by('period')
        
        views_data = {item['period']: item['y'] for item in data}
        
        blog_qs = Blog.objects.all()
        blog_data = blog_qs.annotate(
            period=trunc_func('created_at')
        ).values('period').annotate(
            count=Count('id')
        )
        blogs_map = {item['period']: item['count'] for item in blog_data}
        
        all_periods = sorted(set(views_data.keys()) | set(blogs_map.keys()))
        result = []
        prev_y = 0
        
        for period in all_periods:
            y = views_data.get(period, 0)
            blogs_count = blogs_map.get(period, 0)
            
            if prev_y == 0:
                z = 0 if y == 0 else 100
            else:
                z = ((y - prev_y) / prev_y) * 100
            
            result.append({
                "x": f"{period} (Blogs: {blogs_count})",
                "y": y,
                "z": round(z, 2)
            })
            prev_y = y
            
        return Response(result)
