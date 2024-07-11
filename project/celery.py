from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تعيين إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# استخدام إعدادات Django للتهيئة
app.config_from_object('django.conf:settings', namespace='CELERY')

# اكتشاف المهام في جميع تطبيقات Django
app.autodiscover_tasks()
