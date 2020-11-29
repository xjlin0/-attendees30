from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from attendees.occasions.models import *
from attendees.persons.models import *
from .models import *


class AssemblyAddressInline(admin.TabularInline):
    model = AssemblyAddress
    extra = 0


class AddressAdmin(admin.ModelAdmin):
    inlines = (AssemblyAddressInline,)
    search_fields = ('display_name', 'street1', 'street2', 'city', 'zip_code', 'fields')
    list_display_links = ('street',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'street', 'city', 'zip_code', 'phone1', 'email1')

    def phone1(self, instance):
        return instance.fields['phone1']

    def email1(self, instance):
        return instance.fields['email1']


class DivisionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    list_display_links = ('display_name',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'organization', 'display_name', 'slug', 'modified')


class PropertyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'slug', 'campus', 'modified')


class CampusAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'slug', 'address', 'modified')


class SuiteAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('display_name', 'slug',  'site', 'modified')


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


admin.site.register(Address, AddressAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Suite, SuiteAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Organization, OrganizationAdmin)
