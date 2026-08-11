#!/usr/bin/env python3
"""Send a single plain-text email over SMTP, configured entirely by environment.

Reads its configuration from the environment rather than argv so that message
content never passes through a shell, and so secrets are not visible in the
process table.
"""

import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

REQUIRED = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "MAIL_FROM", "MAIL_TO")


def main():
    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        sys.exit(
            "Missing required configuration: "
            + ", ".join(missing)
            + "\nSet these as repository secrets under "
            "Settings -> Secrets and variables -> Actions."
        )

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT") or 465)
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    message = EmailMessage()
    message["From"] = os.environ["MAIL_FROM"]
    message["To"] = os.environ["MAIL_TO"]
    message["Subject"] = os.environ.get("MAIL_SUBJECT") or "(no subject)"
    message.set_content(os.environ.get("MAIL_BODY") or "")

    context = ssl.create_default_context()

    # Port 465 speaks TLS from the first byte; 587 starts in the clear and is
    # upgraded with STARTTLS. Anything else is assumed to follow the 587 shape.
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
            server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
            server.send_message(message)

    print(f"Sent to {message['To']} via {host}:{port}")


if __name__ == "__main__":
    main()
