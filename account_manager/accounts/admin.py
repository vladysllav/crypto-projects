from django.contrib import admin

from .models import User, Credential, Project, Reminder

admin.site.register(User)
admin.site.register(Credential)
admin.site.register(Project)
admin.site.register(Reminder)
