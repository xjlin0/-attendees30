from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.forms import TextInput
from django.db import models
from mptt.admin import MPTTModelAdmin
from .models import Menu, MenuAuthGroup

from attendees.users.forms.admin_forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name", "organization",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "organization", "is_staff", "is_superuser"]
    search_fields = ["name"]


class MenuAuthGroupInline(admin.TabularInline):
    model = MenuAuthGroup
    extra = 0


@admin.register(Menu)
class MenuAdmin(MPTTModelAdmin):
    readonly_fields = ['id', 'created', 'modified']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100%'})},
    }
    mptt_level_indent = 20
    prepopulated_fields = {"url_name": ("display_name",)}
    list_display = ('display_name', 'is_removed', 'category', 'display_order', 'urn')
    list_editable = ('is_removed', 'display_order')
    inlines = (MenuAuthGroupInline,)
    list_display_links = ('display_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.func.__name__ == 'changelist_view':
            messages.warning(request, 'Not all, but only those records accessible to you will be listed here.')
        return qs.filter(organization=request.user.organization)


@admin.register(MenuAuthGroup)
class MenuAuthGroupAdmin(admin.ModelAdmin):

    list_display = ('auth_group', 'read', 'write', 'menu',)
