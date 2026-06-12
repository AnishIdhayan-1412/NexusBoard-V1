from django.core.exceptions import ValidationError


def validate_image(image):
    # Max size: 5MB
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Image file too large. Maximum size is 5MB.")

    # Allowed extensions
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ext = image.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file type. Allowed: jpg, jpeg, png, gif, webp.")