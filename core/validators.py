from django.core.exceptions import ValidationError
from PIL import Image
import io


def validate_image(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Image file too large. Maximum size is 5MB.")

    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ext = image.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")

    # Validate magic bytes — not just extension
    try:
        image.seek(0)
        img = Image.open(io.BytesIO(image.read()))
        img.verify()
        image.seek(0)
    except Exception:
        raise ValidationError("Invalid or corrupted image file.")