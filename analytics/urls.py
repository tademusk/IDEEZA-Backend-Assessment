from django.urls import path
from .views import BlogViewsAnalytics, TopAnalytics, PerformanceAnalytics

urlpatterns = [
    path('blog-views/', BlogViewsAnalytics.as_view(), name='blog-views'),
    path('top/', TopAnalytics.as_view(), name='top'),
    path('performance/', PerformanceAnalytics.as_view(), name='performance'),
]
