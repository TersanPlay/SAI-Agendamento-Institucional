from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_report_reportexecution'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Report',
        ),
        migrations.DeleteModel(
            name='ReportExecution',
        ),
    ]