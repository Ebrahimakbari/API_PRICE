from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import CustomUserManager
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import logging


logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        
        super().save(*args, **kwargs)
        
        if is_new:
            if self.is_superuser or self.is_staff:
                return
            try:
                current_site = get_current_site(request=None)
                activate_url = f"http://{current_site.domain}{reverse('accounts:activate', kwargs={'token': self.activation_token})}"
                
                # Email content
                subject = 'Activate your account'
                message = f'Hi {self.first_name},\n\nYour account has been created. Please activate your account by clicking the link below:\n\n{activate_url}'
                html_message = f"""
                <html>
                    <body>
                        <h2>Welcome to our platform, {self.first_name}!</h2>
                        <p>Your account has been created. Please activate your account by clicking the button below:</p>
                        <p>
                            <a href="{activate_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px;">
                                Activate Your Account
                            </a>
                        </p>
                        <p>If you didn't create an account, please ignore this email.</p>
                    </body>
                </html>
                """
                self.email_user(
                    subject=subject,
                    message= message,
                    html_message=html_message,
                    from_email= settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[self.email],
                    )
            except Exception as e:
                logger.error(f'Error sending activation email to {self.email}: {str(e)}')
                pass
    
    def get_token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }