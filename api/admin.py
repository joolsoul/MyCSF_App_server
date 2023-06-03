from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User, Map, Schedule, CourseGroup, Publication, Student, Professor, Event


class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student'


class UserAdmin(BaseUserAdmin):
    inlines = (StudentInline,)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "second_name", "patronymic", "email", "phone", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", )}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "email", "first_name", "second_name", "patronymic", "is_verified")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "second_name", "patronymic", "email")
    ordering = ("username",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


class EventAdmin(ModelAdmin):
    list_display = ("title", "event_start_datetime", "event_end_datetime", "is_full_day", "e_type")
    filter_horizontal = ("course_groups", )

class PublicationAdmin(ModelAdmin):
    list_display = ("title", "publication_datetime")

# unreg
admin.site.unregister(Group)
# admin.site.unregister(User)

# reg
admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Map)
admin.site.register(Schedule)
admin.site.register(CourseGroup)
admin.site.register(Event, EventAdmin)
admin.site.register(Publication, PublicationAdmin)

