"""
Models for moreadornexportapp.

Design notes:
- Every string column uses ``TextField`` (no varchar / length limits).
- Primary keys are ``UUIDField`` so IDs are unguessable and globally unique.
- Multiple images / videos per record are stored as a JSON list of base64
  data URI strings (``JSONField(default=list)``). This eliminates the need
  for a separate gallery table — the frontend just iterates the list and
  renders each entry directly. Designed for serverless deploys (Vercel)
  where there's no persistent media folder.
"""

import uuid

from django.db import models


# =====================================================================
# PRODUCT
# =====================================================================
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("textiles", "Textiles & Fabrics"),
        ("electronics", "Electronics & Components"),
        ("machinery", "Industrial Machinery"),
        ("consumer", "Consumer Goods"),
        ("automotive", "Automotive Parts"),
        ("construction", "Construction Materials"),
        ("food", "Food & Beverages"),
        ("medical", "Medical Supplies"),
        ("sports", "Sports & Fitness"),
        ("furniture", "Furniture & Furnishings"),
        ("chemicals", "Chemicals & Raw Materials"),
        ("agricultural", "Agricultural Products"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.TextField()
    description = models.TextField(
        help_text="Short description shown on the product card.",
    )
    details = models.TextField(blank=True, default="")

    category = models.TextField(choices=CATEGORY_CHOICES)
    tags = models.TextField(blank=True, default="")
    moq = models.TextField(blank=True, default="", verbose_name="MOQ")
    lead_time = models.TextField(blank=True, default="")

    # List of base64 data URIs — first entry is the primary card image.
    images = models.JSONField(default=list, blank=True)
    # List of base64 data URIs — optional product videos.
    videos = models.JSONField(default=list, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


# =====================================================================
# MARKET — country / export destination
# =====================================================================
class Market(models.Model):
    REGION_CHOICES = [
        ("north_america", "North America"),
        ("europe", "Europe"),
        ("middle_east", "Middle East"),
        ("east_asia", "East Asia"),
        ("southeast_asia", "Southeast Asia"),
        ("south_asia", "South Asia"),
        ("africa", "Africa"),
        ("oceania", "Oceania"),
        ("south_america", "South America"),
        ("central_america", "Central America"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    country = models.TextField(unique=True)
    code = models.TextField(
        unique=True,
        help_text="3-letter ISO country code (e.g. USA, GBR).",
    )
    flag = models.TextField(help_text="Flag emoji.")
    region = models.TextField(choices=REGION_CHOICES)
    notes = models.TextField(blank=True, default="")

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.flag} {self.country}"


# =====================================================================
# BLOG
# =====================================================================
class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.TextField()
    slug = models.TextField(unique=True, blank=True, default="")
    excerpt = models.TextField()
    body = models.TextField()
    author = models.TextField(default="moreAdorn")
    tags = models.TextField(blank=True, default="")

    # Same list-based pattern as Product: images[0] acts as the hero/cover.
    images = models.JSONField(default=list, blank=True)
    videos = models.JSONField(default=list, blank=True)

    published = models.BooleanField(default=False)
    publish_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publish_date", "-created_at"]

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided.
        if not self.slug:
            from django.utils.text import slugify

            base = slugify(self.title)[:240] or "post"
            slug = base
            i = 2
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


# =====================================================================
# COMPANY CONTACT — singleton (only one row should exist)
# =====================================================================
class CompanyContact(models.Model):
    """Single source of truth for contact details shown on the public site.

    Fed into the Footer, top contact bar, and Contact page. The model is a
    soft-singleton: ``get_solo()`` always returns (and creates if missing)
    the single row.
    """

    DEFAULT_HOURS = [
        {"day": "monday",    "is_open": True,  "open_time": "09:00", "close_time": "18:00"},
        {"day": "tuesday",   "is_open": True,  "open_time": "09:00", "close_time": "18:00"},
        {"day": "wednesday", "is_open": True,  "open_time": "09:00", "close_time": "18:00"},
        {"day": "thursday",  "is_open": True,  "open_time": "09:00", "close_time": "18:00"},
        {"day": "friday",    "is_open": True,  "open_time": "09:00", "close_time": "18:00"},
        {"day": "saturday",  "is_open": True,  "open_time": "10:00", "close_time": "16:00"},
        {"day": "sunday",    "is_open": False, "open_time": "",      "close_time": ""},
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    query_email = models.TextField(blank=True, default="")
    contact_email = models.TextField(blank=True, default="")
    phone = models.TextField(blank=True, default="")

    address = models.TextField(blank=True, default="")
    city = models.TextField(blank=True, default="")
    state = models.TextField(blank=True, default="")
    country = models.TextField(blank=True, default="")
    zip_code = models.TextField(blank=True, default="")
    google_maps_url = models.TextField(blank=True, default="")

    # List of {day, is_open, open_time, close_time}
    business_hours = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Contact"
        verbose_name_plural = "Company Contact"

    def __str__(self) -> str:
        return f"Company Contact ({self.contact_email or 'unset'})"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create(business_hours=cls.DEFAULT_HOURS)
        return obj


# =====================================================================
# SOCIAL MEDIA — singleton storing public profile URLs.
# Empty fields are simply not rendered in the public footer.
# =====================================================================
class SocialMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    facebook_url = models.TextField(blank=True, default="")
    instagram_url = models.TextField(blank=True, default="")
    linkedin_url = models.TextField(blank=True, default="")
    twitter_url = models.TextField(blank=True, default="")
    youtube_url = models.TextField(blank=True, default="")
    whatsapp_url = models.TextField(blank=True, default="")
    telegram_url = models.TextField(blank=True, default="")
    pinterest_url = models.TextField(blank=True, default="")
    github_url = models.TextField(blank=True, default="")
    website_url = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Social Media"
        verbose_name_plural = "Social Media"

    def __str__(self) -> str:
        return "Social Media Links"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


# =====================================================================
# AI SETTINGS — singleton storing the chat assistant configuration.
# The api_key is write-only on the public API (masked on read) so
# nothing leaks to the browser.
# =====================================================================
class AiSettings(models.Model):
    PROVIDER_CHOICES = [
        ("groq", "Groq"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.TextField(choices=PROVIDER_CHOICES, default="groq")
    api_key = models.TextField(blank=True, default="")
    model_name = models.TextField(default="llama-3.3-70b-versatile")
    assistant_name = models.TextField(default="Aria")
    welcome_message = models.TextField(
        default=(
            "Hi 👋  I'm Aria — Moreadorn's trade assistant. Ask me about our "
            "products, shipping destinations, or compliance."
        ),
    )
    enabled = models.BooleanField(default=False)
    max_output_tokens = models.IntegerField(default=800)
    temperature = models.FloatField(default=0.4)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Settings"
        verbose_name_plural = "AI Settings"

    def __str__(self) -> str:
        return f"AI Settings ({self.provider} / {self.model_name})"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


# =====================================================================
# AI API KEY — multiple keys can be saved, but only ONE may be active
# at a time. The chat view reads whichever row is active=True.
# =====================================================================
class AiApiKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.TextField(help_text="Human-friendly name, e.g. 'Production'.")
    api_key = models.TextField()
    model_name = models.TextField(default="llama-3.3-70b-versatile")
    active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI API Key"
        verbose_name_plural = "AI API Keys"

    def __str__(self) -> str:
        return f"{self.label} ({'active' if self.active else 'inactive'})"

    @classmethod
    def get_active(cls):
        return cls.objects.filter(active=True).first()


# =====================================================================
# EMAIL CONFIG — list of saved SMTP credentials with single-active rule.
# The active row is used to send all transactional email (contact /
# quote thank-you mails). Mirrors the `AiApiKey` pattern so admins can
# rotate accounts without redeploying.
# =====================================================================
class EmailConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.TextField(
        help_text="Human-friendly name, e.g. 'Production Gmail'.",
    )
    email = models.TextField(
        help_text="The Gmail / SMTP address that emails are sent from.",
    )
    app_password = models.TextField(
        help_text="Gmail app password (or SMTP password). Stored encrypted-at-rest by the DB.",
    )
    host = models.TextField(default="smtp.gmail.com")
    port = models.IntegerField(default=587)
    use_tls = models.BooleanField(default=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Config"
        verbose_name_plural = "Email Configs"

    def __str__(self) -> str:
        return f"{self.label} ({'active' if self.active else 'inactive'})"

    @classmethod
    def get_active(cls):
        return cls.objects.filter(active=True).first()


# =====================================================================
# REQUEST QUOTE — unified model for product quotes, contact-form
# enquiries, and "Get Quote" info requests. Distinguished by
# `category_name` so the admin can filter / triage by source.
# =====================================================================
class RequestQuote(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("quoted", "Quoted"),
        ("closed", "Closed"),
    ]

    CATEGORY_CHOICES = [
        ("product", "Product"),
        ("contact", "ContactUs"),
        ("info", "RequestInfoQuote"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source category — populated by the originating form on the public site.
    category_name = models.TextField(
        choices=CATEGORY_CHOICES,
        default="product",
    )

    product = models.ForeignKey(
        Product,
        related_name="quote_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # All snapshot / contact fields are optional — only the basics
    # (name, email, description) are guaranteed. Each form sends what it has.
    product_name = models.TextField(blank=True, default="")
    quantity = models.TextField(blank=True, default="")

    name = models.TextField()
    whatsapp = models.TextField(blank=True, default="")
    phone = models.TextField(blank=True, default="")
    email = models.TextField()

    country = models.TextField(blank=True, default="")
    city = models.TextField(blank=True, default="")
    state = models.TextField(blank=True, default="")
    zip_code = models.TextField(blank=True, default="")
    address = models.TextField(blank=True, default="")
    description = models.TextField()

    status = models.TextField(choices=STATUS_CHOICES, default="new")
    admin_notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Request Quote"
        verbose_name_plural = "Request Quotes"

    def __str__(self) -> str:
        suffix = self.product_name or self.get_category_name_display()
        return f"{self.name} — {suffix}"
