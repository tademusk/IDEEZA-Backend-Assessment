from django.core.management.base import BaseCommand
from analytics.models import Country, User, Blog, View
from django.utils import timezone
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        # Create Countries
        countries = ['USA', 'UK', 'Canada', 'Germany', 'France']
        country_objs = []
        for name in countries:
            c, created = Country.objects.get_or_create(name=name)
            country_objs.append(c)
            
        # Create Users
        users = []
        for i in range(10):
            u, created = User.objects.get_or_create(
                name=f'User {i}',
                country=random.choice(country_objs)
            )
            users.append(u)
            
        # Create Blogs
        blogs = []
        for i in range(20):
            b, created = Blog.objects.get_or_create(
                title=f'Blog Post {i}',
                user=random.choice(users)
            )
            # Set created_at randomly within last year
            b.created_at = timezone.now() - timedelta(days=random.randint(0, 365))
            b.save()
            blogs.append(b)
            
        # Create Views
        for b in blogs:
            # Random views for each blog
            for _ in range(random.randint(5, 50)):
                v = View.objects.create(
                    blog=b,
                    timestamp=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                
        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
