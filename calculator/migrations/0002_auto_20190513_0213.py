# Generated by Django 2.2.1 on 2019-05-13 02:13

import calculator.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='id',
            field=models.CharField(default=calculator.models.increment_loan_id, editable=False, max_length=19, primary_key=True, serialize=False),
        ),
    ]