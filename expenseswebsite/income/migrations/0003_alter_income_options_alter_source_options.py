# Generated by Django 5.0.2 on 2024-03-31 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0002_alter_source_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='income',
            options={'ordering': ['-income_date'], 'verbose_name_plural': 'Income'},
        ),
        migrations.AlterModelOptions(
            name='source',
            options={},
        ),
    ]
