from django.contrib import admin

from .models import (
    AiApiKey,
    AiSettings,
    Blog,
    CompanyContact,
    EmailConfig,
    Market,
    Product,
    RequestQuote,
    SocialMedia,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "active", "created_at")
    list_filter = ("active", "category")
    search_fields = ("name", "description", "tags")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("flag", "country", "code", "region", "active", "created_at")
    list_filter = ("active", "region")
    search_fields = ("country", "code")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published", "publish_date")
    list_filter = ("published",)
    search_fields = ("title", "excerpt", "tags", "author")
    readonly_fields = ("id", "slug", "created_at", "updated_at")


@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ("contact_email", "phone", "city", "country", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Emails & Phone", {"fields": ("query_email", "contact_email", "phone")}),
        (
            "Address",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "country",
                    "zip_code",
                    "google_maps_url",
                )
            },
        ),
        ("Business Hours", {"fields": ("business_hours",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        # Singleton — only allow creating the first row.
        return not CompanyContact.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "created_at", "updated_at")

    def has_add_permission(self, request):
        return not SocialMedia.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AiSettings)
class AiSettingsAdmin(admin.ModelAdmin):
    list_display = ("provider", "model_name", "assistant_name", "enabled", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")

    def has_add_permission(self, request):
        return not AiSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AiApiKey)
class AiApiKeyAdmin(admin.ModelAdmin):
    list_display = ("label", "model_name", "active", "created_at")
    list_filter = ("active",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ("label", "email", "host", "port", "active", "created_at")
    list_filter = ("active",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(RequestQuote)
class RequestQuoteAdmin(admin.ModelAdmin):
    list_display = ("name", "category_name", "product_name", "email", "status", "created_at")
    list_filter = ("category_name", "status", "country")
    search_fields = ("name", "email", "phone", "product_name", "description")
    readonly_fields = ("id", "created_at", "updated_at")
    list_editable = ("status",)
    fieldsets = (
        ("Source", {"fields": ("category_name",)}),
        ("Product", {"fields": ("product", "product_name")}),
        ("Customer", {"fields": ("name", "email", "phone", "whatsapp", "quantity")}),
        ("Address", {"fields": ("country", "state", "city", "zip_code", "address")}),
        ("Request", {"fields": ("description",)}),
        ("Internal", {"fields": ("status", "admin_notes")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
