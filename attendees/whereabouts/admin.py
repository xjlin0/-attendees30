from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from attendees.occasions.models import *
from attendees.persons.models import *
from .models import *


class PlaceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('display_name',)
    list_display_links = ('id',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'display_name', 'subject', 'street')


class DivisionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    list_display_links = ('display_name',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'organization', 'display_name', 'slug', 'modified')


class PropertyAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'display_name', 'slug', 'campus', 'modified')


class CampusAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'slug', 'modified')


class SuiteAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'display_name', 'slug',  'site', 'modified')


class RoomAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'label', 'suite', 'accessibility', 'modified')


class OrganizationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'slug', 'infos', 'modified')


admin.site.register(Place, PlaceAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Suite, SuiteAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Organization, OrganizationAdmin)
