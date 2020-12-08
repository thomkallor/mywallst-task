from __future__ import unicode_literals
from django.db import migrations, models
from stripeapp.subscription.models import User


def forwards_func(apps, schema_editor):
    User.objects.create_superuser('admin', 'password')


def reverse_func(apps, schema_editor):
    User.objects.get(username='admin').delete()


class Migration(migrations.Migration):
    dependencies = [('subscription', '0001_initial')]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
