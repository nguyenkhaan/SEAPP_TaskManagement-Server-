import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to, subject, html):
    message = Mail(
        from_email=os.getenv("MAIL_DEFAULT_SENDER_2"),
        to_emails=to,
        subject=subject,
        html_content=html
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY_2"))
        response = sg.send(message)
        return {"success": True, "status": response.status_code}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
