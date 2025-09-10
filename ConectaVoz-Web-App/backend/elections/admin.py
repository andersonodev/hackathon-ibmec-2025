from django.contrib import admin
from .models import ConnectaAssignment, ConnectaProfile

@admin.register(ConnectaAssignment)
class ConnectaAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'connecta', 'assigned_at', 'is_active']
    list_filter = ['is_active', 'assigned_at', 'connecta']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__username',
                     'connecta__first_name', 'connecta__last_name', 'connecta__username']
    readonly_fields = ['assigned_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'connecta')


@admin.register(ConnectaProfile)
class ConnectaProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_available', 'current_assignments', 'max_assignments', 'is_at_capacity']
    list_filter = ['is_available', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'current_assignments', 'is_at_capacity']
    
    fieldsets = (
        ('Informações do Conecta', {
            'fields': ('user', 'bio', 'specialties')
        }),
        ('Disponibilidade', {
            'fields': ('is_available', 'max_assignments', 'current_assignments', 'is_at_capacity')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
