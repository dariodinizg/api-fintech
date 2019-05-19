# Generated by Django 2.2.1 on 2019-05-18 01:19

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='rate_adjust',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Real Tax'),
        ),
    ]