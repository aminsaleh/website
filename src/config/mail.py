from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template import loader
from types import SimpleNamespace


class Mail:
    
    def __init__(self, user, url) -> None:
        self.user = user
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.context = {
            "url": url,
            "username": self.user.username,
            "token": token,
            "uid": uid,
        }

    def __call__(self):
        html_content = loader.get_template('mail_content.html')
        
        subject = 'Confirmation Email'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [self.user.email, ]

        from loguru import logger
        logger.info(html_content.render(self.context))
        
        # send_mail(subject, html_content.render(context), email_from, recipient_list)
