from django.contrib import admin
from .models import Lead, LeadActivity

class LeadActivityInline(admin.TabularInline):
    model = LeadActivity
    extra = 0
    readonly_fields = ('user', 'action', 'old_status', 'new_status', 'note', 'created_at')
    can_delete = False

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'source', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('name', 'email', 'phone', 'source')
    inlines = [LeadActivityInline]
    date_hierarchy = 'created_at'

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'action', 'old_status', 'new_status', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('lead__name', 'note')
