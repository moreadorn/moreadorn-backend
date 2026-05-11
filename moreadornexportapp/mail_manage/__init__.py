"""
Email templates and send logic for moreadornexportapp.

Note: Python module names cannot contain hyphens, so this folder is named
`mail_manage` (underscore). Functionally it serves as the requested
"mail-manage" folder — all email-related code lives here.
"""

from .contact_email import send_contact_thank_you_email  # re-export
from .quote_email import send_quote_thank_you_email  # re-export

__all__ = [
    "send_contact_thank_you_email",
    "send_quote_thank_you_email",
]
