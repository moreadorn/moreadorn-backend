"""Serializers for moreadornexportapp.

`FileListToDataURIField` is the key piece — it accepts repeated multipart
file uploads (e.g. multiple ``images=...`` parts) and converts each one
to a base64 data URI string. The result is stored in the model's
``JSONField`` as a list. On read it returns the list as-is, so the
frontend just iterates and renders each entry.
"""

from __future__ import annotations

import base64

from rest_framework import serializers

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


def _file_to_data_uri(file_obj) -> str:
    content_type = (
        getattr(file_obj, "content_type", None) or "application/octet-stream"
    )
    payload = file_obj.read()
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


class FileListToDataURIField(serializers.Field):
    """List of files (or pre-encoded data URI strings) → list of data URIs."""

    default_error_messages = {
        "invalid": "Upload one or more valid files.",
    }

    def get_value(self, dictionary):
        # Multipart submissions repeat the field name once per file. Use
        # ``getlist`` so we receive every uploaded file rather than just
        # the last one.
        if hasattr(dictionary, "getlist"):
            values = dictionary.getlist(self.field_name)
            if values:
                return values
        return dictionary.get(self.field_name, serializers.empty)

    def to_representation(self, value):
        return list(value or [])

    def to_internal_value(self, data):
        if data in (None, "", "null"):
            return []

        # Normalise single value → list
        if not isinstance(data, list):
            data = [data]

        out: list[str] = []
        for item in data:
            if not item or item in ("null", "undefined"):
                continue
            if isinstance(item, str):
                if item.startswith("data:"):
                    out.append(item)  # already encoded
                # plain strings that aren't data URIs are ignored
                continue
            if hasattr(item, "read"):
                out.append(_file_to_data_uri(item))
            else:
                self.fail("invalid")
        return out


# =====================================================================
# PRODUCT
# =====================================================================
class ProductSerializer(serializers.ModelSerializer):
    images = FileListToDataURIField(required=False)
    videos = FileListToDataURIField(required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "details",
            "category",
            "tags",
            "moq",
            "lead_time",
            "images",
            "videos",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =====================================================================
# MARKET
# =====================================================================
class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = [
            "id",
            "country",
            "code",
            "flag",
            "region",
            "notes",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =====================================================================
# BLOG
# =====================================================================
class BlogSerializer(serializers.ModelSerializer):
    images = FileListToDataURIField(required=False)
    videos = FileListToDataURIField(required=False)

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "body",
            "author",
            "tags",
            "images",
            "videos",
            "published",
            "publish_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


# =====================================================================
# COMPANY CONTACT
# =====================================================================
class CompanyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyContact
        fields = [
            "id",
            "query_email",
            "contact_email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "zip_code",
            "google_maps_url",
            "business_hours",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


# =====================================================================
# SOCIAL MEDIA
# =====================================================================
class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = [
            "id",
            "facebook_url",
            "instagram_url",
            "linkedin_url",
            "twitter_url",
            "youtube_url",
            "whatsapp_url",
            "telegram_url",
            "pinterest_url",
            "github_url",
            "website_url",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


# =====================================================================
# AI SETTINGS — ``api_key`` is masked on read, write-only on update.
# Admins can verify the last 4 chars without ever exposing the full key.
# =====================================================================
class AiSettingsSerializer(serializers.ModelSerializer):
    api_key = serializers.SerializerMethodField()
    api_key_input = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Set this to a new key to overwrite. Leave blank to keep existing.",
    )
    api_key_set = serializers.SerializerMethodField()

    class Meta:
        model = AiSettings
        fields = [
            "id",
            "provider",
            "model_name",
            "assistant_name",
            "welcome_message",
            "enabled",
            "max_output_tokens",
            "temperature",
            "api_key",
            "api_key_input",
            "api_key_set",
            "updated_at",
        ]
        read_only_fields = ["id", "api_key", "api_key_set", "updated_at"]

    def get_api_key(self, obj) -> str:
        # Never return the raw key. Return only a short masked preview.
        k = obj.api_key or ""
        if not k:
            return ""
        if len(k) <= 8:
            return "••••••••"
        return f"{k[:4]}••••••••{k[-4:]}"

    def get_api_key_set(self, obj) -> bool:
        return bool(obj.api_key)

    def update(self, instance, validated_data):
        new_key = validated_data.pop("api_key_input", None)
        if new_key is not None and new_key != "":
            instance.api_key = new_key
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


# =====================================================================
# AI API KEY — list of saved keys with single-active enforcement.
# `api_key` is masked on read, set via the write-only `api_key_input` field.
# =====================================================================
class AiApiKeySerializer(serializers.ModelSerializer):
    api_key = serializers.SerializerMethodField()
    api_key_input = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="Set this to a new key. Required on create, optional on update.",
    )

    class Meta:
        model = AiApiKey
        fields = [
            "id",
            "label",
            "model_name",
            "active",
            "api_key",
            "api_key_input",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "api_key", "created_at", "updated_at"]

    def get_api_key(self, obj) -> str:
        k = obj.api_key or ""
        if not k:
            return ""
        if len(k) <= 8:
            return "••••••••"
        return f"{k[:4]}••••••••{k[-4:]}"

    def validate(self, attrs):
        # Single-active rule. Reject the request if the new/updated row is
        # active=True and a *different* row is already active.
        instance = self.instance
        new_active = attrs.get(
            "active",
            instance.active if instance is not None else False,
        )
        if new_active:
            existing = AiApiKey.objects.filter(active=True)
            if instance is not None:
                existing = existing.exclude(pk=instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    "active": (
                        "Another API key is already active. Deactivate or "
                        "delete it first, then activate this one. Only one "
                        "key may be active at a time."
                    )
                })
        return attrs

    def create(self, validated_data):
        new_key = validated_data.pop("api_key_input", None)
        if not new_key:
            raise serializers.ValidationError({
                "api_key_input": "An API key value is required when adding a new key.",
            })
        validated_data["api_key"] = new_key
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_key = validated_data.pop("api_key_input", None)
        if new_key is not None and new_key != "":
            instance.api_key = new_key
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


# =====================================================================
# EMAIL CONFIG — single-active SMTP credentials.
# `app_password` is masked on read, set via the write-only
# `app_password_input` field.
# =====================================================================
class EmailConfigSerializer(serializers.ModelSerializer):
    app_password = serializers.SerializerMethodField()
    app_password_input = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="App password. Required on create, optional on update.",
    )

    class Meta:
        model = EmailConfig
        fields = [
            "id",
            "label",
            "email",
            "host",
            "port",
            "use_tls",
            "active",
            "app_password",
            "app_password_input",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "app_password", "created_at", "updated_at"]

    def get_app_password(self, obj) -> str:
        # Mask the password — only show last 2 chars so the admin can verify
        # the right one is saved without leaking the full secret.
        p = obj.app_password or ""
        if not p:
            return ""
        if len(p) <= 4:
            return "••••"
        return f"••••••••{p[-2:]}"

    def validate(self, attrs):
        # Single-active rule. Reject if another config is already active.
        instance = self.instance
        new_active = attrs.get(
            "active",
            instance.active if instance is not None else False,
        )
        if new_active:
            existing = EmailConfig.objects.filter(active=True)
            if instance is not None:
                existing = existing.exclude(pk=instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    "active": (
                        "Another email config is already active. Deactivate "
                        "or delete it first, then activate this one. Only one "
                        "config may be active at a time."
                    )
                })
        return attrs

    def create(self, validated_data):
        new_password = validated_data.pop("app_password_input", None)
        if not new_password:
            raise serializers.ValidationError({
                "app_password_input": (
                    "An app password is required when adding a new config."
                ),
            })
        validated_data["app_password"] = new_password
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_password = validated_data.pop("app_password_input", None)
        if new_password is not None and new_password != "":
            instance.app_password = new_password
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


# =====================================================================
# REQUEST QUOTE — unified product / contact / info-quote serializer
# =====================================================================
class RequestQuoteSerializer(serializers.ModelSerializer):
    # Validate as email even though the underlying column is plain text.
    email = serializers.EmailField()
    product_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequestQuote
        fields = [
            "id",
            "category_name",
            "product",
            "product_name",
            "product_image",
            "name",
            "quantity",
            "whatsapp",
            "phone",
            "email",
            "country",
            "city",
            "state",
            "zip_code",
            "address",
            "description",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_image", "created_at", "updated_at"]
        extra_kwargs = {
            # Most contact channels submit a subset of these — make every
            # snapshot / address field tolerant of being absent on POST.
            "product_name": {"required": False, "allow_blank": True},
            "quantity": {"required": False, "allow_blank": True},
            "phone": {"required": False, "allow_blank": True},
            "country": {"required": False, "allow_blank": True},
            "city": {"required": False, "allow_blank": True},
            "state": {"required": False, "allow_blank": True},
            "zip_code": {"required": False, "allow_blank": True},
            "address": {"required": False, "allow_blank": True},
            "whatsapp": {"required": False, "allow_blank": True},
            "category_name": {"required": False},
        }

    def get_product_image(self, obj):
        if obj.product and obj.product.images:
            return obj.product.images[0]
        return None

    def validate(self, attrs):
        """For contact-form submissions, reject if the same email / phone /
        WhatsApp number is already on file. Prevents the same visitor from
        spamming the public contact form. Product / info requests are
        allowed to repeat (a buyer may legitimately enquire about multiple
        SKUs from the same address).
        """
        category = attrs.get("category_name") or "product"
        if category == "contact" and self.instance is None:
            checks = [
                ("email", attrs.get("email"), "email address"),
                ("phone", attrs.get("phone"), "phone number"),
                ("whatsapp", attrs.get("whatsapp"), "WhatsApp number"),
            ]
            duplicates: dict[str, str] = {}
            qs = RequestQuote.objects.filter(category_name="contact")
            for field, value, label in checks:
                if not value:
                    continue
                if qs.filter(**{field: value}).exists():
                    duplicates[field] = (
                        f"This {label} has already been submitted. "
                        "Our team will get back to you shortly — please "
                        "wait for our reply before submitting again."
                    )
            if duplicates:
                raise serializers.ValidationError(duplicates)
        return attrs

    def create(self, validated_data):
        product = validated_data.get("product")
        if product and not validated_data.get("product_name"):
            validated_data["product_name"] = product.name
        return super().create(validated_data)
