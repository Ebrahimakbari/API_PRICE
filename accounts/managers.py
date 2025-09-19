from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, phone_number, username, first_name, last_name):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')

        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            username = username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, phone_number, username, first_name, last_name):
        user = self.create_user(
            email,
            password=password,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
