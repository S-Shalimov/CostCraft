from django.db import migrations, models
import django.db.models.deletion
import json
from decimal import Decimal
from pathlib import Path


def load_seed_data_rate(apps, schema_editor):
    ExchangeRate = apps.get_model('DxfEstimate', 'ExchangeRate')
    path_to_data = str(Path(__file__).parent) + '\\seed_data\\seed_data_rate.json'
    with open(path_to_data, encoding='utf-8-sig') as f:
        seed_data = json.load(f)
    for obj in seed_data:
        ExchangeRate.objects.create(**obj['fields'])

def load_seed_data_units(apps, schema_editor):
    Units = apps.get_model('DxfEstimate', 'Units')
    path_to_data = str(Path(__file__).parent) + '\\seed_data\\seed_data_units.json'
    with open(path_to_data, encoding='utf-8-sig') as f:
        seed_data = json.load(f)
    for obj in seed_data:
        Units.objects.create(**obj['fields'])

def load_seed_data_types(apps, schema_editor):
    Types = apps.get_model('DxfEstimate', 'Types')
    path_to_data = str(Path(__file__).parent) + '\\seed_data\\seed_data_types.json'
    with open(path_to_data, encoding='utf-8-sig') as f:
        seed_data = json.load(f)
    for obj in seed_data:
        Types.objects.create(**obj['fields'])

def load_seed_data_pricebase(apps, schema_editor):
    BasePrice = apps.get_model('DxfEstimate', 'BasePrice')
    path_to_data = str(Path(__file__).parent) + '\\seed_data\\seed_data_pricebase.json'
    Units = apps.get_model('DxfEstimate', 'Units')
    Types = apps.get_model('DxfEstimate', 'Types')
    foreign_values = {
        'units': {
            'meters': Units.objects.get(pk=1),
            'square_meters': Units.objects.get(pk=2),
            'pieces': Units.objects.get(pk=3)
        },
        'types': {
            'листовой': Types.objects.get(pk=2),
            'работы': Types.objects.get(pk=3),
            'деталь': Types.objects.get(pk=4)
        }
    }
    BasePrice.objects.create(name='Доска', units=foreign_values['units']['square_meters'], price_sum=500000,
                             price_dol=Decimal(45.0),
                             types=foreign_values['types']['листовой'])
    BasePrice.objects.create(name='Лазерная резка', units=foreign_values['units']['meters'], price_sum=300000,
                             price_dol=Decimal(25.0),
                             types=foreign_values['types']['работы'])
    BasePrice.objects.create(name='Диод', units=foreign_values['units']['pieces'], price_sum=500000,
                             price_dol=Decimal(45.0),
                             types=foreign_values['types']['работы'])


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BasePrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('price_sum', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=20, null=True)),
                ('price_dol', models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Types',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('types', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('units', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Estimate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=15)),
                ('units', models.CharField(blank=True, max_length=10)),
                ('types', models.CharField(blank=True, max_length=50)),
                ('price_dol', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='name_set', to='DxfEstimate.baseprice')),
            ],
        ),
        migrations.AddField(
            model_name='baseprice',
            name='types',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DxfEstimate.types'),
        ),
        migrations.AddField(
            model_name='baseprice',
            name='units',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DxfEstimate.units'),
        ),
        migrations.RunPython(load_seed_data_units),
        migrations.RunPython(load_seed_data_types),
        migrations.RunPython(load_seed_data_rate),
        migrations.RunPython(load_seed_data_pricebase),
    ]
