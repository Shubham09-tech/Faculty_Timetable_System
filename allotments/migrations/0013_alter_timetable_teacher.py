# Generated by Django 5.1.4 on 2025-02-06 12:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allotments', '0012_alter_timetable_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='allotments.teacher'),
        ),
    ]
