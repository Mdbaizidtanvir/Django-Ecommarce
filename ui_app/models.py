from django.db import models
from cloudinary.models import CloudinaryField


class Banner(models.Model):
    # For Slider
    slider_image_1 = CloudinaryField(blank=True, null=True)
    slider_image_1_url = models.URLField(blank=True, null=True)

    slider_image_2 = CloudinaryField(blank=True, null=True)
    slider_image_2_url = models.URLField(blank=True, null=True)

    slider_image_3 = CloudinaryField(blank=True, null=True)
    slider_image_3_url = models.URLField(blank=True, null=True)

    # For Grid
    grid_image_1 = CloudinaryField(blank=True, null=True)
    grid_image_1_url = models.URLField(blank=True, null=True)

    grid_image_2 = CloudinaryField(blank=True, null=True)
    grid_image_2_url = models.URLField(blank=True, null=True)

    # Store / Redirect URL (for click-through link)
    redirect_url = models.CharField(default="/store")

    def get_image(self, cloudinary_field, url_field):
        """Helper: Return Cloudinary image if exists, else fallback to URL"""
        if cloudinary_field:
            return cloudinary_field.url
        elif url_field:
            return url_field
        return ""

    def get_slider_images(self):
        """Return all slider images as a list"""
        return [
            self.get_image(self.slider_image_1, self.slider_image_1_url),
            self.get_image(self.slider_image_2, self.slider_image_2_url),
            self.get_image(self.slider_image_3, self.slider_image_3_url),
        ]

    def get_grid_images(self):
        """Return both grid images"""
        return [
            self.get_image(self.grid_image_1, self.grid_image_1_url),
            self.get_image(self.grid_image_2, self.grid_image_2_url),
        ]

    def __str__(self):
        return f"Banner #{self.id}"



class SiteSettings(models.Model):
    # Branding
    site_name = models.CharField(max_length=150, default="My Website")
    logo = CloudinaryField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    # Secondary image (favicon / default SEO / secondary logo)
    secondary_image = CloudinaryField(blank=True, null=True)
    secondary_image_url = models.URLField(blank=True, null=True)

    # Social Links
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    messanger = models.URLField(blank=True, null=True)
    wahtsapp = models.URLField(blank=True, null=True)

    # SEO / Meta
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=300, blank=True, null=True)

    # Contact Info
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Helpers
    def get_logo(self):
        if self.logo:
            return self.logo.url
        elif self.logo_url:
            return self.logo_url
        return ""

    def get_secondary_image(self):
        if self.secondary_image:
            return self.secondary_image.url
        elif self.secondary_image_url:
            return self.secondary_image_url
        return ""

    def __str__(self):
        return f"Site Settings ({self.site_name})"





class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    banner = CloudinaryField(blank=True, null=True)
    link = models.CharField(max_length=900,blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_running(self):
        from django.utils import timezone
        return self.is_active and self.start_date <= timezone.now() <= self.end_date
