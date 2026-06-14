from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_shopsettings_payment_card_holder_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address_label',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Manzil nomi'),
        ),
    ]
