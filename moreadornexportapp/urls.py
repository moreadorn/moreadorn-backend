from django.urls import path

from .cron_views import DBHealthCronView
from .views import (
    HealthCheckView,
    AdminLoginView,
    AdminLogoutView,
    AdminMeView,
    AdminResetPasswordView,
    AdminResetUsernameView,
    AiApiKeyDetailView,
    AiApiKeyListCreateView,
    AiChatView,
    AiSettingsView,
    BlogDetailView,
    BlogListCreateView,
    CompanyContactView,
    CreateSuperuserView,
    EmailConfigDetailView,
    EmailConfigListCreateView,
    MarketDetailView,
    MarketListCreateView,
    ProductDetailView,
    ProductListCreateView,
    RequestQuoteDetailView,
    RequestQuoteListCreateView,
    SocialMediaView,
)

urlpatterns = [
    # ----- Public health check -----
    path("health/", HealthCheckView.as_view(), name="health-check"),

    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<uuid:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("markets/", MarketListCreateView.as_view(), name="market-list-create"),
    path("markets/<uuid:pk>/", MarketDetailView.as_view(), name="market-detail"),
    path("blogs/", BlogListCreateView.as_view(), name="blog-list-create"),
    path("blogs/<uuid:pk>/", BlogDetailView.as_view(), name="blog-detail"),
    path(
        "request-quotes/",
        RequestQuoteListCreateView.as_view(),
        name="request-quote-list-create",
    ),
    path(
        "request-quotes/<uuid:pk>/",
        RequestQuoteDetailView.as_view(),
        name="request-quote-detail",
    ),
    path("company-contact/", CompanyContactView.as_view(), name="company-contact"),
    path("social-media/", SocialMediaView.as_view(), name="social-media"),
    path("ai-settings/", AiSettingsView.as_view(), name="ai-settings"),
    path("ai-keys/", AiApiKeyListCreateView.as_view(), name="ai-keys"),
    path("ai-keys/<uuid:pk>/", AiApiKeyDetailView.as_view(), name="ai-key-detail"),
    path("ai-chat/", AiChatView.as_view(), name="ai-chat"),
    path("email-configs/", EmailConfigListCreateView.as_view(), name="email-config-list-create"),
    path(
        "email-configs/<uuid:pk>/",
        EmailConfigDetailView.as_view(),
        name="email-config-detail",
    ),
    # ----- Admin auth -----
    path("create-superuser/", CreateSuperuserView.as_view(), name="create-superuser"),
    path("admin-login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin-logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("admin-me/", AdminMeView.as_view(), name="admin-me"),
    path(
        "admin-reset-username/",
        AdminResetUsernameView.as_view(),
        name="admin-reset-username",
    ),
    path(
        "admin-reset-password/",
        AdminResetPasswordView.as_view(),
        name="admin-reset-password",
    ),
    # ----- Cron jobs (hit by Vercel scheduler) -----
    path("cron/db-health/", DBHealthCronView.as_view(), name="cron-db-health"),
]
