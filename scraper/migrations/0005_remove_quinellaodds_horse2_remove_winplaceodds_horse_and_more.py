# Generated by Django 5.2.1 on 2025-06-23 02:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0004_horse_quinellaodds_race_winplaceodds_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quinellaodds',
            name='horse2',
        ),
        migrations.RemoveField(
            model_name='winplaceodds',
            name='horse',
        ),
        migrations.RemoveField(
            model_name='quinellaodds',
            name='horse1',
        ),
        migrations.AlterUniqueTogether(
            name='quinellaodds',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='quinellaodds',
            name='race',
        ),
        migrations.RemoveField(
            model_name='winplaceodds',
            name='race',
        ),
        migrations.AlterUniqueTogether(
            name='winplaceodds',
            unique_together=None,
        ),
        migrations.DeleteModel(
            name='Horse',
        ),
        migrations.DeleteModel(
            name='QuinellaOdds',
        ),
        migrations.DeleteModel(
            name='Race',
        ),
        migrations.DeleteModel(
            name='WinPlaceOdds',
        ),
    ]
