from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import  Topic, Redactor, Newspaper


admin.site.register(Topic)


@admin.register(Redactor)
class RedactorAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("years_of_experience", )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": ("years_of_experience", "first_name", "last_name")},
        ),
    )


@admin.register(Newspaper)
class NewspaperAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "published_date")
    filter_horizontal = ("publishers",)
