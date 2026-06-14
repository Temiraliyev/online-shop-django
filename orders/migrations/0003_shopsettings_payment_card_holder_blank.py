from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_address_order_city_order_delivery_cost_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_address', models.TextField(
                    default="Toshkent, O'zbekiston",
                    verbose_name="Do'kon manzili",
                    help_text="Do'kon joylashgan to'liq manzil (geocoding uchun ishlatiladi)"
                )),
                ('shop_lat', models.FloatField(
                    default=41.2995,
                    verbose_name="Do'kon kengligi (lat)",
                    help_text="Google Maps yoki Yandex Maps dan olish mumkin"
                )),
                ('shop_lon', models.FloatField(
                    default=69.2401,
                    verbose_name="Do'kon uzunligi (lon)"
                )),
                ('cost_per_km', models.IntegerField(
                    default=1000,
                    verbose_name="1 km uchun narx (so'm)"
                )),
                ('min_delivery_cost', models.IntegerField(
                    default=10000,
                    verbose_name="Minimal yetkazib berish narxi (so'm)"
                )),
            ],
            options={
                'verbose_name': "Do'kon sozlamalari",
                'verbose_name_plural': "Do'kon sozlamalari",
            },
        ),
        migrations.AlterField(
            model_name='payment',
            name='card_holder',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
