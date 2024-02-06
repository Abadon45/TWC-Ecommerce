import os
from django.utils import timezone

def upload_image_path_admin(instance, filename):
    # Get the current date and time
    now = timezone.now()

    # Extract the file extension from the filename
    _, ext = os.path.splitext(filename)

    # Generate a new filename using the current timestamp
    filename = f"admin_images/{now.strftime('%Y/%m/%d/%H%M%S')}{ext}"

    # Return the complete path for the uploaded image
    return filename

def upload_image_path(instance, filename):
    # Get the current date and time
    now = timezone.now()

    # Extract the file extension from the filename
    _, ext = os.path.splitext(filename)
    
    username = instance.username

    # Generate a new filename using the current timestamp
    filename = f"user_images/{username}/{now.strftime('%Y/%m/%d/%H%M%S')}{ext}"

    # Return the complete path for the uploaded image
    return filename

