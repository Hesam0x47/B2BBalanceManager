# Generated by Django 4.2.16 on 2024-11-03 21:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balanceincreaserequestmodel',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balance_increase_request', to='accounts.sellerprofile'),
        ),
        migrations.AlterField(
            model_name='chargecustomermodel',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charge_customer', to='accounts.sellerprofile'),
        ),
    ]