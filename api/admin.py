from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import Group
from django.forms import ModelForm

from .models import User, Map, Schedule, CourseGroup, Publication, Student, Professor

# Register your models here.
# admin.site.register(User)


# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('get_user', 'year_of_enrollment', 'record_book_number', "course_group")
#
#     @admin.display()
#     def get_user(self, obj):
#         return obj.user
#
# admin.site.register(Student, StudentAdmin)

class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student'

class UserAdmin(ModelAdmin):
    inlines = (StudentInline,)


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
admin.site.register(Publication)

