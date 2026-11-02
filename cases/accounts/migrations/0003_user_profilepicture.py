# Generated for profilePicture
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_passwordresetcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profilePicture',
            field=models.ImageField(blank=True, help_text='Profile picture', null=True, upload_to='profile_photos/'),
        ),
    ]
