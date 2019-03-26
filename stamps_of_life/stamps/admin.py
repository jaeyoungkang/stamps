from django.contrib import admin
from .models import Stamp

class StampAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','removed_at')

admin.site.register(Stamp,StampAdmin)
