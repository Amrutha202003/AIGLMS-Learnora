from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(request, user):
    token = default_token_generator.make_token(user)

    verification_url = request.build_absolute_uri(
        reverse('verify_email', args=[user.pk, token])
    )

    send_mail(
        "Verify Your Account",
        f"Click the link to verify your account:\n{verification_url}",
        None,
        [user.email],
    )