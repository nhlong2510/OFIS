# Generated by Django 4.0.6 on 2022-10-11 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opera', '0003_alter_flipinfo_foliono'),
    ]

    operations = [
        migrations.AddField(
            model_name='flipinfo',
            name='NetAmount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='flipinfo',
            name='FolioNo',
            field=models.CharField(blank=True, default=0, max_length=500, null=True),
        ),
    ]
