from django.contrib import admin
from .models import Banner, SiteSettings

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "redirect_url")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone")


from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "start_date", "end_date")
    list_filter = ("is_active",)
    search_fields = ("title",)
