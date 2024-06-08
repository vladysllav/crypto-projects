from django.contrib import admin

from .models import Credential, Project, Task

admin.site.register(Credential)
admin.site.register(Project)
admin.site.register(Task)
