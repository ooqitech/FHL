import logging
from typing import Union

import yagmail
from celery import shared_task
from django.conf import settings

logger = logging.getLogger('app')


@shared_task
def send_email(email_to: Union[str, list], subject: str, contents: Union[str, list] = '',
               attachments=None, cc=None, bcc=None):
    """
    Send email
    Args:
        subject: 邮件主题
        email_to: 收件人/收件人列表
        contents: list/str
        attachments: 附件
        cc: Carbon copy
        bcc: Blind carbon copy

    Returns:
        Bool refer to sent status

    """
    try:
        yag = yagmail.SMTP(user=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD,
                           host=settings.EMAIL_HOST)
        yag.send(to=email_to, subject=subject, contents=contents, attachments=attachments, cc=cc, bcc=bcc)
        return True
    except Exception as e:
        logger.error(f'发送邮件失败: {e}')
        return False
