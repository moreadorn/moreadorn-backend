"""
Send the thank-you email for a *contact-form* submission (i.e.
``category_name == "contact"``). The product/info "quote request" path uses
``quote_email.py`` instead.

The HTML body is kept inline below as ``EMAIL_TEMPLATE`` (Django template
syntax) and rendered with the visitor's submitted details. Sent as a
multipart message through the Gmail SMTP backend configured in
``settings.py``.

A static demo of this template lives next to it as
``contact_thank_you.html`` for browser preview.
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
# EMAIL TEMPLATE — Django template syntax. Internal CSS only (mail-safe).
# =====================================================================
EMAIL_TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>Thank you for contacting {{ site_name }}</title>
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

      .section { padding: 18px 32px; }
      .section-title { font-size: 11px; letter-spacing: 0.28em; text-transform: uppercase; color: #C8A96A; font-weight: 700; margin: 0 0 14px; display: flex; align-items: center; gap: 10px; }
      .section-title:before, .section-title:after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, transparent, rgba(200, 169, 106, 0.4), transparent); }

      .detail-card { background: #FAF8F3; border: 1px solid #EFE7D4; border-radius: 12px; padding: 4px 4px; }
      .detail-row { padding: 12px 18px; border-bottom: 1px solid #EFE7D4; }
      .detail-row:last-child { border-bottom: 0; }
      .detail-label { font-size: 10px; color: #9CA3AF; letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; margin: 0 0 4px; }
      .detail-value { font-size: 14px; color: #0B0B0B; font-weight: 500; line-height: 1.5; margin: 0; word-break: break-word; }

      .promise { background: linear-gradient(135deg, rgba(200, 169, 106, 0.10), rgba(230, 211, 163, 0.04)); border-left: 4px solid #C8A96A; padding: 18px 22px; border-radius: 8px; margin: 0; }
      .promise-title { font-size: 14px; font-weight: 700; color: #0B0B0B; margin: 0 0 6px; }
      .promise-text { font-size: 13px; color: #4B5563; line-height: 1.6; margin: 0; }

      .timeline { padding: 0 32px 8px; }
      .timeline-step { display: flex; gap: 14px; padding: 12px 0; }
      .timeline-num { flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #C8A96A, #E6D3A3); color: #0B0B0B; font-weight: 800; font-size: 12px; line-height: 28px; text-align: center; }
      .timeline-text { font-size: 13px; color: #4B5563; line-height: 1.55; }
      .timeline-text strong { color: #0B0B0B; }

      .cta { text-align: center; padding: 20px 32px 32px; }
      .cta-button { display: inline-block; background: linear-gradient(135deg, #C8A96A 0%, #E6D3A3 100%); color: #0B0B0B !important; font-size: 13px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; padding: 14px 32px; border-radius: 999px; text-decoration: none; box-shadow: 0 6px 20px rgba(200, 169, 106, 0.3); }

      .footer { background: #0B0B0B; padding: 26px 32px; text-align: center; color: #6B7280; font-size: 12px; line-height: 1.7; }
      .footer-brand { color: #FFFFFF; font-weight: 700; letter-spacing: 0.04em; margin: 0 0 6px; }
      .footer-link { color: #C8A96A; text-decoration: none; }

      @media only screen and (max-width: 620px) {
        .wrapper { padding: 16px 8px; }
        .header, .hero, .section, .cta, .footer, .timeline { padding-left: 22px !important; padding-right: 22px !important; }
        .hero-title { font-size: 22px !important; }
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
            <span class="badge">Message Received</span>
            <h1 class="hero-title">Thank you for reaching out, {{ customer_name }}.</h1>
            <p class="hero-subtitle">
              We have received your message and a member of our trade desk
              will review it personally. You can expect a reply from us within
              <strong style="color:#0B0B0B;">2–3 business days</strong>.
            </p>
          </td>
        </tr>

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
              {% if phone %}
              <div class="detail-row">
                <p class="detail-label">Phone</p>
                <p class="detail-value">{{ phone }}</p>
              </div>
              {% endif %}
              {% if whatsapp %}
              <div class="detail-row">
                <p class="detail-label">WhatsApp</p>
                <p class="detail-value">{{ whatsapp }}</p>
              </div>
              {% endif %}
              {% if location %}
              <div class="detail-row">
                <p class="detail-label">Location</p>
                <p class="detail-value">{{ location }}</p>
              </div>
              {% endif %}
              <div class="detail-row">
                <p class="detail-label">Your Message</p>
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
                A trade specialist will read your enquiry, gather any
                background needed, and get in touch with you within
                <strong>2–3 business days</strong> over email, phone, or
                WhatsApp — whichever you prefer.
              </p>
            </div>
          </td>
        </tr>

        <tr>
          <td class="timeline">
            <div class="timeline-step">
              <div class="timeline-num">1</div>
              <div class="timeline-text">
                <strong>Today</strong> — your message lands in our inbox and is
                acknowledged by this email.
              </div>
            </div>
            <div class="timeline-step">
              <div class="timeline-num">2</div>
              <div class="timeline-text">
                <strong>Within 24 hours</strong> — a trade specialist is
                assigned and begins reviewing your requirements.
              </div>
            </div>
            <div class="timeline-step">
              <div class="timeline-num">3</div>
              <div class="timeline-text">
                <strong>Within 2–3 business days</strong> — you will hear back
                from us with a tailored response.
              </div>
            </div>
          </td>
        </tr>

        <tr>
          <td class="cta">
            <p style="margin:0 0 14px; color:#6B7280; font-size:13px;">
              Need to add anything to your message in the meantime?
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
              You're receiving this because you contacted us via the website
              contact form. This is an automated acknowledgement — a personal
              reply will follow shortly.
            </p>
          </td>
        </tr>
      </table>
    </div>
  </body>
</html>"""


def _build_context(quote) -> dict:
    """Translate a RequestQuote (category=contact) into template variables."""

    # Local import to avoid AppRegistryNotReady during migrations.
    from ..models import CompanyContact

    company = CompanyContact.get_solo()
    company_email = company.contact_email or get_active_from_email()
    company_office = ", ".join(
        v for v in [company.city, company.state, company.country] if v
    ) or "Ahmedabad, Gujarat, India"

    location = ", ".join(
        v for v in [quote.city, quote.state, quote.country] if v
    )

    return {
        "site_name": getattr(settings, "SITE_NAME", "Moreadorn"),
        "site_tagline": getattr(settings, "SITE_TAGLINE", "Global Trade Co."),
        "site_url": getattr(settings, "SITE_URL", ""),
        "from_email": company_email,
        "company_office": company_office,
        "company_phone": company.phone,
        "customer_name": quote.name,
        "email": quote.email,
        "phone": quote.phone,
        "whatsapp": quote.whatsapp,
        "location": location,
        "description": quote.description,
    }


def _render_html(context: dict) -> str:
    return Template(EMAIL_TEMPLATE).render(Context(context))


def _send_now(quote) -> None:
    try:
        context = _build_context(quote)
        html_body = _render_html(context)
        text_body = strip_tags(html_body)

        subject = f"Thank you for contacting {context['site_name']}"
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
        logger.info("Contact thank-you email sent to %s", quote.email)
    except Exception:  # pragma: no cover
        logger.exception("Failed to send contact thank-you email to %s", quote.email)


def send_contact_thank_you_email(quote) -> None:
    """Fire-and-forget send — backgrounded so the API response isn't held up."""
    thread = threading.Thread(target=_send_now, args=(quote,), daemon=True)
    thread.start()
