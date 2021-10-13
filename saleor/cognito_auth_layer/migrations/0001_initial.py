# Generated by Django 3.1.2 on 2021-07-07 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CognitoUserJwt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('saleor_jwt', models.TextField()),
            ],
        ),
        migrations.AddIndex(
            model_name='cognitouserjwt',
            index=models.Index(fields=['username'], name='cognito_aut_usernam_814415_idx'),
        ),
    ]
