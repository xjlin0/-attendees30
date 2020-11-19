from django.db.models import Q
from django_summernote.admin import SummernoteModelAdmin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from django.contrib import messages
from django.contrib import admin
from attendees.occasions.models import *
from attendees.whereabouts.models import *
from .models import *

# Register your models here.


class AttendeeAddressInline(admin.StackedInline):
    model = AttendeeAddress
    extra = 0


class AttendingMeetInline(admin.StackedInline):
    model = AttendingMeet
    extra = 0


class RelationshipInline(admin.TabularInline):
    model = Relationship
    fk_name = 'from_attendee'
    extra = 0


class FamilyAttendeeInline(admin.TabularInline):
    model = FamilyAttendee
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'created', 'modified']
    prepopulated_fields = {"slug": ("display_name",)}
    list_display = ('id', 'display_name', 'slug', 'display_order', 'description', 'modified')


class FamilyAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('display_name', 'infos')
    readonly_fields = ['id', 'created', 'modified']
    inlines = (FamilyAttendeeInline,)
    list_display_links = ('id',)
    list_display = ('id', 'display_name', 'infos', 'division', 'created')
    fieldsets = (
        (None, {"fields": (tuple(['display_name', 'display_order', 'division']),
                           tuple(['infos']),
                           tuple(['id', 'created', 'modified']),
                           ), }),
    )


class FamilyAttendeeAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'family', 'attendee', 'role', 'modified')


class RelationAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'created', 'modified']
    list_display_links = ('title',)
    list_display = ('id', 'title', 'reciprocal_ids', 'emergency_contact', 'scheduler', 'relative', 'display_order')


class AttendeeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('first_name', 'last_name', 'last_name2', 'first_name2')
    readonly_fields = ['id', 'created', 'modified']
    inlines = (AttendeeAddressInline, RelationshipInline)
    list_display_links = ('id',)
    list_display = ('id', 'division', 'first_name', 'last_name', 'last_name2', 'first_name2', 'progressions', 'infos')

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     if not request.user.is_superuser and request.resolver_match.func.__name__ == 'changelist_view':
    #         messages.warning(request, 'Not all, but only attendees in your organization will be shown here.')
    #     Todo: maybe if their families in the other organization?
    #         return qs.filter(division__organization=request.user.organization)
    #     else:
    #         return qs


class RegistrationAdmin(admin.ModelAdmin):
    # list_per_page = 1000
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    list_display_links = ('main_attendee',)
    list_display = ('id', 'main_attendee', 'assembly', 'infos', 'modified')


class AttendanceInline(admin.StackedInline):
    model = Attendance
    extra = 0


class AttendingAdmin(admin.ModelAdmin):
    # list_per_page = 1000
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('attendee__first_name', 'attendee__last_name', 'attendee__first_name2', 'attendee__last_name2')
    list_display_links = ('attendee',)
    list_filter = ('meets',)
    readonly_fields = ['id', 'created', 'modified']
    inlines = (AttendingMeetInline,) # add AttendanceInline when creating new Attending will fails on meet_names
    list_display = ('id', 'registration', 'attendee', 'meet_names')


class NoteAdmin(SummernoteModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('body',)
    readonly_fields = ['id', 'created', 'modified']
    summernote_fields = ('body',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'category', 'content_object', 'display_order', 'modified')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.resolver_match.func.__name__ == 'changelist_view':
            messages.warning(request, 'Not all, but only those notes accessible to you will be listed here.')
        if request.user.is_counselor():
            return qs.filter(
                        ~Q(category='counseling')
                          |
                        (Q(category='counseling') and (Q(infos__can_access__contains=request.user.attendee_uuid_str())
                                                       |
                                                       Q(infos__can_access__contains=Note.ALL_COUNSELORS))
                         )
            )
        return qs.exclude(category=Note.COUNSELING)


class RelationshipAdmin(admin.ModelAdmin):
    list_display_links = ('relation',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'from_attendee', 'relation', 'to_attendee', 'emergency_contact', 'scheduler', 'in_family', 'finish')


class AttendingMeetAdmin(admin.ModelAdmin):
    list_display_links = ('attending',)
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'attending', 'meet', 'character', 'category', 'finish', 'modified')


class FamilyAddressAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'created', 'modified']
    list_display = ('id', 'family', 'address', 'created', 'modified')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Attendee, AttendeeAdmin)
admin.site.register(FamilyAttendee, FamilyAttendeeAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Attending, AttendingAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(AttendingMeet, AttendingMeetAdmin)
admin.site.register(FamilyAddress, FamilyAddressAdmin)
