# Generated by Django 2.2 on 2019-04-29 15:51

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyWords',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=200, unique=True)),
                ('idf', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('max_keyword_nb', models.IntegerField(blank=True, null=True)),
                ('real_name', models.CharField(blank=True, max_length=100, null=True)),
                ('infos', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Series',
            },
        ),
        migrations.CreateModel(
            name='Posting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('tf', models.FloatField(null=True)),
                ('keywords', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recommandation.KeyWords')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recommandation.Series')),
            ],
        ),
        migrations.AddField(
            model_name='keywords',
            name='series',
            field=models.ManyToManyField(through='recommandation.Posting', to='recommandation.Series'),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(choices=[('1', "J'aime"), ('0', "Je n'aime pas")], max_length=1)),
                ('serie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recommandation.Series')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('rating', 'serie', 'user')},
            },
        ),
    ]
