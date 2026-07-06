from rest_framework import serializers
import os


def validate_image(image):

    allowed_extensions = [".jpg", ".jpeg", ".png"]

    extension = os.path.splitext(image.name)[1].lower()

    if extension not in allowed_extensions:
        raise serializers.ValidationError(
            "Only JPG, JPEG and PNG images are allowed."
        )

    return image