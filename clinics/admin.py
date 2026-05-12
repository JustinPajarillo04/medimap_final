from django.contrib import admin
from .models import Clinic


class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact', 'status', 'rating')
    search_fields = ('name', 'address', 'services')
    list_filter = ('status',)


admin.site.register(Clinic, ClinicAdmin)

