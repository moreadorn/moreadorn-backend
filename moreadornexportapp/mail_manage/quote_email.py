"""
Send the thank-you email to a customer who submitted a Product Quote Request.

The HTML body is kept inline below as `EMAIL_TEMPLATE` (Django template
syntax). It is rendered with the customer's submitted details and sent as
multipart through the Gmail SMTP backend configured in settings.py.

`quote_thank_you.html` in this folder is a static DEMO version of the email
(rendered with sample data) that you can open in a browser to preview the
design. The actual outgoing email always uses the template below.
"""

from __future__ import annotations

import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.utils.html import strip_tags

from .smtp import (
    get_active_from_email,
    get_default_from_address,
    get_smtp_connection,
)

logger = logging.getLogger(__name__)


# =====================================================================
# EMAIL TEMPLATE — Django template syntax. Internal CSS only (mail safe).
# Edit here to change the email design. The DEMO file in this folder is
# regenerated whenever you edit the demo content separately for preview.
# =====================================================================
EMAIL_TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>Thank you for your quote request — {{ site_name }}</title>
    <style>
      body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
      table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-collapse: collapse; }
      img { -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; display: block; }
      body { margin: 0 !important; padding: 0 !important; width: 100% !important; }
      a { color: #C8A96A; text-decoration: none; }

      .wrapper { background: #F4F1EA; padding: 32px 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #2B2B2B; }
      .container { max-width: 620px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(11, 11, 11, 0.06); }

      .header { background: linear-gradient(135deg, #0B0B0B 0%, #1a1a1a 100%); padding: 36px 32px 32px; text-align: center; position: relative; }
      .brand-mark { width: 56px; height: 56px; margin: 0 auto 14px; background: linear-gradient(135deg, #C8A96A 0%, #E6D3A3 100%); border-radius: 14px; line-height: 56px; text-align: center; color: #0B0B0B; font-size: 22px; font-weight: 800; letter-spacing: 1px; }
      .brand-name { font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.04em; margin: 0; }
      .brand-tagline { font-size: 11px; color: #C8A96A; letter-spacing: 0.32em; text-transform: uppercase; margin: 6px 0 0; font-weight: 600; }

      .hero { padding: 36px 32px 24px; text-align: center; }
      .badge { display: inline-block; padding: 6px 14px; background: #FAF6EC; color: #C8A96A; font-size: 10px; letter-spacing: 0.28em; text-transform: uppercase; font-weight: 700; border-radius: 999px; border: 1px solid rgba(200, 169, 106, 0.3); }
      .hero-title { font-size: 26px; line-height: 1.25; color: #0B0B0B; font-weight: 800; margin: 18px 0 10px; letter-spacing: -0.01em; }
      .hero-subtitle { font-size: 15px; line-height: 1.6; color: #6B7280; margin: 0; }

      .section { padding: 20px 32px; }
      .section-title { font-size: 11px; letter-spacing: 0.28em; text-transform: uppercase; color: #C8A96A; font-weight: 700; margin: 0 0 14px; display: flex; align-items: center; gap: 10px; }
      .section-title:before, .section-title:after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(200, 169, 106, 0.4), transparent); }

      .detail-card { background: #FAF8F3; border: 1px solid #EFE7D4; border-radius: 12px; padding: 4px 4px; }
      .detail-row { padding: 12px 18px; border-bottom: 1px solid #EFE7D4; }
      .detail-row:last-child { border-bottom: 0; }
      .detail-label { font-size: 10px; color: #9CA3AF; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; margin: 0 0 4px; }
      .detail-value { font-size: 14px; color: #0B0B0B; font-weight: 500; line-height: 1.5; margin: 0; word-break: break-word; }

      .product-card { background: linear-gradient(135deg, #0B0B0B 0%, #1f1f1f 100%); color: #FFFFFF; border-radius: 12px; padding: 22px; }
      .product-eyebrow { font-size: 10px; letter-spacing: 0.28em; text-transform: uppercase; color: #C8A96A; font-weight: 700; margin: 0 0 8px; }
      .product-name { font-size: 18px; font-weight: 800; margin: 0 0 6px; line-height: 1.3; }
      .product-meta { font-size: 13px; color: #C8A96A; margin: 0; }

      .promise { background: linear-gradient(135deg, rgba(200, 169, 106, 0.08), rgba(230, 211, 163, 0.04)); border-left: 4px solid #C8A96A; padding: 18px 22px; border-radius: 8px; margin: 0; }
      .promise-title { font-size: 14px; font-weight: 700; color: #0B0B0B; margin: 0 0 6px; }
      .promise-text { font-size: 13px; color: #4B5563; line-height: 1.6; margin: 0; }

      .cta { text-align: center; padding: 26px 32px 32px; }
      .cta-button { display: inline-block; background: linear-gradient(135deg, #C8A96A 0%, #E6D3A3 100%); color: #0B0B0B !important; font-size: 13px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; padding: 14px 32px; border-radius: 999px; text-decoration: none; box-shadow: 0 6px 20px rgba(200, 169, 106, 0.3); }

      .footer { background: #0B0B0B; padding: 26px 32px; text-align: center; color: #6B7280; font-size: 12px; line-height: 1.7; }
      .footer-brand { color: #FFFFFF; font-weight: 700; letter-spacing: 0.04em; margin: 0 0 6px; }
      .footer-link { color: #C8A96A; text-decoration: none; }

      @media only screen and (max-width: 620px) {
        .wrapper { padding: 16px 8px; }
        .header, .hero, .section, .cta, .footer { padding-left: 22px !important; padding-right: 22px !important; }
        .hero-title { font-size: 22px !important; }
        .product-name { font-size: 16px !important; }
      }
    </style>
  </head>
  <body class="wrapper">
    <div class="wrapper">
      <table role="presentation" class="container" width="100%" cellspacing="0" cellpadding="0">
        <tr>
          <td class="header">
            <div class="brand-mark">M</div>
            <p class="brand-name">{{ site_name|upper }}</p>
            <p class="brand-tagline">{{ site_tagline }}</p>
          </td>
        </tr>

        <tr>
          <td class="hero">
            <span class="badge">Quote Request Received</span>
            <h1 class="hero-title">Thank you, {{ customer_name }}!</h1>
            <p class="hero-subtitle">
              We've received your product enquiry and our trade desk is already
              reviewing it. You'll hear back from us within
              <strong style="color:#0B0B0B;">2–3 business days</strong>
              with a tailored quotation.
            </p>
          </td>
        </tr>

        {% if product_name %}
        <tr>
          <td class="section">
            <p class="section-title"><span>{% if category_name == "product" %}Product Enquired{% else %}Subject{% endif %}</span></p>
            <div class="product-card">
              <p class="product-eyebrow">Item</p>
              <p class="product-name">{{ product_name }}</p>
              {% if quantity %}<p class="product-meta">Quantity requested: {{ quantity }}</p>{% endif %}
            </div>
          </td>
        </tr>
        {% endif %}

        <tr>
          <td class="section">
            <p class="section-title"><span>Your Submitted Details</span></p>
            <div class="detail-card">
              <div class="detail-row">
                <p class="detail-label">Full Name</p>
                <p class="detail-value">{{ customer_name }}</p>
              </div>
              <div class="detail-row">
                <p class="detail-label">Email</p>
                <p class="detail-value">{{ email }}</p>
              </div>
              <div class="detail-row">
                <p class="detail-label">Phone</p>
                <p class="detail-value">{{ phone }}</p>
              </div>
              {% if whatsapp %}
              <div class="detail-row">
                <p class="detail-label">WhatsApp</p>
                <p class="detail-value">{{ whatsapp }}</p>
              </div>
              {% endif %}
              {% if quantity %}
              <div class="detail-row">
                <p class="detail-label">Quantity</p>
                <p class="detail-value">{{ quantity }}</p>
              </div>
              {% endif %}
              <div class="detail-row">
                <p class="detail-label">Delivery Address</p>
                <p class="detail-value">
                  {% if address %}{{ address }}<br />{% endif %}
                  {{ city }}{% if state %}, {{ state }}{% endif %}{% if zip_code %} - {{ zip_code }}{% endif %}<br />
                  {{ country }}
                </p>
              </div>
              <div class="detail-row">
                <p class="detail-label">Your Requirements</p>
                <p class="detail-value">{{ description|linebreaksbr }}</p>
              </div>
            </div>
          </td>
        </tr>

        <tr>
          <td class="section">
            <div class="promise">
              <p class="promise-title">What happens next?</p>
              <p class="promise-text">
                Our trade desk will verify product specifications, source the
                best supplier match, and prepare a detailed quotation including
                pricing, lead time, and shipping options. Expect to hear from
                us within <strong>2-3 business days</strong>.
              </p>
            </div>
          </td>
        </tr>

        <tr>
          <td class="cta">
            <p style="margin:0 0 14px; color:#6B7280; font-size:13px;">
              Need to update your request or share more context?
            </p>
            <a href="mailto:{{ from_email }}" class="cta-button">Reply to this email</a>
          </td>
        </tr>

        <tr>
          <td class="footer">
            <p class="footer-brand">{{ site_name|upper }}</p>
            <p style="margin:0 0 6px;">{{ site_tagline }} - {{ company_office }}</p>
            <p style="margin:0;">
              {% if site_url %}<a href="{{ site_url }}" class="footer-link">{{ site_url }}</a>&nbsp;-&nbsp;{% endif %}
              <a href="mailto:{{ from_email }}" class="footer-link">{{ from_email }}</a>
              {% if company_phone %}&nbsp;-&nbsp;<a href="tel:{{ company_phone }}" class="footer-link">{{ company_phone }}</a>{% endif %}
            </p>
            <p style="margin:14px 0 0; font-size:11px; color:#4B5563;">
              You're receiving this because you submitted a product quote
              request on our website. This is an automated confirmation - a
              human reply will follow shortly.
            </p>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>"""


def _build_context(quote) -> dict:
    """Translate a ProductQuoteRequest model instance into template variables.

    Company contact details (footer email + office line) are pulled live
    from the CompanyContact singleton so admin edits flow through to all
    outgoing thank-you emails without code changes.
    """
    # Local import keeps this module importable when models aren't yet
    # ready (e.g. during migrations).
    from ..models import CompanyContact

    company = CompanyContact.get_solo()
    # The visible "from" address shown inside the email body — prefer the
    # public contact_email; if none, fall back to whichever sender account
    # is currently active (DB EmailConfig or .env).
    company_email = company.contact_email or get_active_from_email()
    company_office = ", ".join(
        v for v in [company.city, company.state, company.country] if v
    ) or "Ahmedabad, Gujarat, India"

    return {
        "site_name": getattr(settings, "SITE_NAME", "Moreadorn"),
        "site_tagline": getattr(settings, "SITE_TAGLINE", "Global Trade Co."),
        "site_url": getattr(settings, "SITE_URL", ""),
        "from_email": company_email,
        "company_office": company_office,
        "company_phone": company.phone,
        "category_name": getattr(quote, "category_name", "product"),
        "customer_name": quote.name,
        "email": quote.email,
        "phone": quote.phone,
        "whatsapp": quote.whatsapp,
        "quantity": quote.quantity,
        "country": quote.country,
        "city": quote.city,
        "state": quote.state,
        "zip_code": quote.zip_code,
        "address": quote.address,
        "description": quote.description,
        # Empty string for non-product enquiries — the template hides the
        # product card entirely when this is blank.
        "product_name": quote.product_name or (
            quote.product.name if quote.product else ""
        ),
    }


def _render_html(context: dict) -> str:
    """Render the embedded EMAIL_TEMPLATE with the given context."""
    return Template(EMAIL_TEMPLATE).render(Context(context))


def _send_now(quote) -> None:
    """Synchronous send. Called from a background thread."""
    try:
        context = _build_context(quote)
        html_body = _render_html(context)
        text_body = strip_tags(html_body)

        subject = (
            f"Thank you for your quote request - {context['product_name']}"
            if context.get("product_name")
            else "Thank you for getting in touch with Moreadorn"
        )
        # Prefer the admin-configured email (DB row) over the .env default.
        from_email = get_default_from_address() or settings.DEFAULT_FROM_EMAIL
        reply_to_address = get_active_from_email() or settings.EMAIL_HOST_USER
        to = [quote.email]

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=to,
            reply_to=[reply_to_address] if reply_to_address else None,
            connection=get_smtp_connection(),
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Quote thank-you email sent to %s", quote.email)
    except Exception:  # pragma: no cover
        logger.exception("Failed to send quote thank-you email to %s", quote.email)


def send_quote_thank_you_email(quote) -> None:
    """
    Fire-and-forget send. Spawns a daemon thread so the API response isn't
    held up by Gmail SMTP latency (typically 1-3 seconds).
    """
    thread = threading.Thread(target=_send_now, args=(quote,), daemon=True)
    thread.start()
