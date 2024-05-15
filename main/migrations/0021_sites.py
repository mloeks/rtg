from django.db import migrations


def load_initial_data(apps, schema_editor):
    sites_model = apps.get_model('sites', 'Site')
    sites_model.objects.all().delete()
    sites_model.objects.create(pk=1, domain="localhost:3000", name="RTG (LOCAL)")
    sites_model.objects.create(pk=2, domain="demo.royale-tippgemeinschaft.de", name="RTG (DEMO)")
    sites_model.objects.create(pk=3, domain="www.royale-tippgemeinschaft.de", name="RTG")


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('main', '0020_auto_20180901_1050'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
