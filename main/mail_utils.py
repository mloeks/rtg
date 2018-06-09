from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from main.models import User
from main.utils import active_users


def send_post_as_mail(post_instance):
    undisclosed_recipients = settings.EMAIL_UNDISCLOSED_RECIPIENTS
    subject, from_email = settings.EMAIL_PREFIX + post_instance.title, settings.DEFAULT_FROM_EMAIL

    if post_instance.force_all_users:
        target_users = User.objects.exclude(email=None).exclude(email='')
    elif post_instance.force_active_users:
        target_users = active_users().exclude(email=None).exclude(email='')
    elif post_instance.force_inactive_users:
        target_users = User.objects.filter(is_active=True).filter(last_login__isnull=True)
    else:
        target_users = active_users().exclude(email=None).exclude(email='').filter(profile__daily_emails=True)

    recipients = list(usr.email for usr in target_users)
    recipients.extend(list(usr.profile.email2 for usr in target_users if usr.profile.email2))
    admin_recipients = [tpl[1] for tpl in settings.ADMINS]

    text_content = post_instance.content
    html_content = with_rtg_template({'subtitle': 'Königliche Mitteilung', 'content': post_instance.content})

    if undisclosed_recipients:
        recipients.extend(admin_recipients)
        msg = EmailMultiAlternatives(subject, text_content, from_email, bcc=recipients)
    else:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=recipients, bcc=admin_recipients)

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def with_rtg_template(context):
    return render_to_string('rtg/mail_template.html', context)
