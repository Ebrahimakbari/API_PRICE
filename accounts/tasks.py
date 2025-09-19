from celery import shared_task
import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)



@shared_task
def send_token_to_email(email, subject, message, html_message):
    try:
        send_mail(
            subject=subject,
            message= message,
            html_message=html_message,
            from_email= settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info(f'Sent code to email {email}')
        return True
    except Exception as e:
        logger.error(f'Error sending code to email {email}: {str(e)}')
        return False