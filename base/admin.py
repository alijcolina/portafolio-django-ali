from django.contrib import admin
from .models import Profile, Post, Tag, PostComment
from django.contrib.auth.models import Group

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
    list_display = ('post', 'created')
    list_filter = ('created',)

# Desregistrar Group para evitar el error 500 en el admin
admin.site.unregister(Group)