# Generated by Django 2.1.5 on 2019-01-14 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommandation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posting',
            name='tf',
            field=models.DecimalField(db_index=True, decimal_places=40, max_digits=40, null=True),
        ),
    ]