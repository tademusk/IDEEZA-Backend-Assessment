from django.contrib import admin
from .models import Country, User, Blog, View

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)
    raw_id_fields = ('country',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'user__name')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'

@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('blog__title',)
    raw_id_fields = ('blog',)
    date_hierarchy = 'timestamp'
