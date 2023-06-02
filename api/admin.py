from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, Map, Schedule, CourseGroup, Publication, Event

# Register your models here.
admin.site.register(User)
admin.site.register(Map)
admin.site.register(Schedule)
admin.site.register(CourseGroup)
admin.site.register(Publication)
admin.site.register(Event)
admin.site.unregister(Group)