# Generated by Django 4.2 on 2023-06-03 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitnessmanager_api', '0003_course_courseschedule_room_reservation_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'verbose_name': 'Curso', 'verbose_name_plural': 'Cursos'},
        ),
        migrations.AlterModelOptions(
            name='courseinstance',
            options={'verbose_name': 'Instancia del Curso', 'verbose_name_plural': 'Instancias de los Cursos'},
        ),
        migrations.AlterModelOptions(
            name='courseschedule',
            options={'verbose_name': 'Horario del Curso', 'verbose_name_plural': 'Horarios de los Cursos'},
        ),
        migrations.AlterModelOptions(
            name='gym',
            options={'verbose_name': 'Gimnasio', 'verbose_name_plural': 'Gimnasios'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['created_at'], 'verbose_name': 'Mensaje', 'verbose_name_plural': 'Mensajes'},
        ),
        migrations.AlterModelOptions(
            name='reservation',
            options={'verbose_name': 'Reserva', 'verbose_name_plural': 'Reservas'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'Sala', 'verbose_name_plural': 'Salas'},
        ),
        migrations.AlterField(
            model_name='customer',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='Dirección de correo electrónico'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='passport_number',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Número de Pasaporte'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='customer_profile_pictures', verbose_name='Foto de Perfil'),
        ),
        migrations.AlterField(
            model_name='gym',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Dirección del Gimnasio'),
        ),
        migrations.AlterField(
            model_name='gym',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Nombre del Gimnasio'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha del Pago'),
        ),
    ]
