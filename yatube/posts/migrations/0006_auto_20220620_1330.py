# Generated by Django 2.2.16 on 2022-06-20 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(
                blank=True,
                help_text='Группа, к которой будет относиться пост',
                null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='group_posts', to='posts.Group',
                verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(
                help_text='Текст нового поста',
                verbose_name='Текст поста'),
        ),
    ]
