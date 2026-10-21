from django.contrib import admin
from .models import Profile, Post, Tag, PostComment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'user')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('headline', 'active', 'featured', 'created')
    list_filter = ('active', 'featured', 'created')
    search_fields = ('headline', 'body')
    prepopulated_fields = {'slug': ('headline',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created')
    list_filter = ('created',)