from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_likes'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100, verbose_name='Manzil nomi')),
                ('full_address', models.TextField(verbose_name="To'liq manzil")),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lon', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_addresses', to='accounts.user')),
            ],
            options={
                'verbose_name': 'Saqlangan manzil',
                'verbose_name_plural': 'Saqlangan manzillar',
                'ordering': ('-created',),
            },
        ),
    ]
