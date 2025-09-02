from .models import SiteSettings

def site_settings(request):
    # Always return the latest settings
    settings = SiteSettings.objects.last()
    return {
        "settings": settings
    }
