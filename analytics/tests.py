from django.test import TestCase, Client
from django.urls import reverse
from .models import Country, User, Blog, View
from django.utils import timezone
from datetime import timedelta

class AnalyticsAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.country = Country.objects.create(name="Test Country")
        self.user = User.objects.create(name="Test User", country=self.country)
        self.blog = Blog.objects.create(title="Test Blog", user=self.user)
        self.view = View.objects.create(blog=self.blog)
        
    def test_blog_views_user(self):
        response = self.client.get(reverse('blog-views'), {'object_type': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['x'], 'Test User')
        self.assertEqual(response.data[0]['y'], 1)
        self.assertEqual(response.data[0]['z'], 1)

    def test_blog_views_country(self):
        response = self.client.get(reverse('blog-views'), {'object_type': 'country'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['x'], 'Test Country')

    def test_top_blogs(self):
        response = self.client.get(reverse('top'), {'top': 'blog'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['x'], 'Test Blog')
        
    def test_performance(self):
        response = self.client.get(reverse('performance'), {'compare': 'year'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        
    def test_dynamic_filter(self):
        response = self.client.get(reverse('top'), {'top': 'blog', 'title__icontains': 'Test'})
        self.assertEqual(len(response.data), 1)
        
        response = self.client.get(reverse('top'), {'top': 'blog', 'title__icontains': 'NonExistent'})
        self.assertEqual(len(response.data), 0)

    def test_or_logic(self):
        Blog.objects.create(title="Another Post", user=self.user)
        
        response = self.client.get(reverse('top'), {
            'top': 'blog',
            'or__title__icontains': 'Test',
            'or__user__name__icontains': 'NonExistent'
        })
        self.assertEqual(len(response.data), 1)
        
        response = self.client.get(reverse('top'), {
            'top': 'blog',
            'or__title__icontains': 'NonExistent',
            'or__user__name__icontains': 'AlsoFake'
        })
        self.assertEqual(len(response.data), 0)

class EdgeCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_blog_views_missing_object_type(self):
        response = self.client.get(reverse('blog-views'))
        self.assertEqual(response.status_code, 400)
    
    def test_blog_views_invalid_object_type(self):
        response = self.client.get(reverse('blog-views'), {'object_type': 'invalid'})
        self.assertEqual(response.status_code, 400)
    
    def test_top_missing_parameter(self):
        response = self.client.get(reverse('top'))
        self.assertEqual(response.status_code, 400)
    
    def test_top_invalid_type(self):
        response = self.client.get(reverse('top'), {'top': 'invalid'})
        self.assertEqual(response.status_code, 400)
    
    def test_performance_missing_compare(self):
        response = self.client.get(reverse('performance'))
        self.assertEqual(response.status_code, 400)
    
    def test_performance_invalid_compare(self):
        response = self.client.get(reverse('performance'), {'compare': 'invalid'})
        self.assertEqual(response.status_code, 400)
    
    def test_empty_database(self):
        response = self.client.get(reverse('blog-views'), {'object_type': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        response = self.client.get(reverse('top'), {'top': 'blog'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        
        response = self.client.get(reverse('performance'), {'compare': 'month'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
    
    def test_not_filter(self):
        country = Country.objects.create(name="USA")
        user = User.objects.create(name="John", country=country)
        Blog.objects.create(title="Test Blog", user=user)
        
        response = self.client.get(reverse('top'), {
            'top': 'blog',
            'not__title__icontains': 'Test'
        })
        self.assertEqual(len(response.data), 0)

