import random
import string
from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    """
    Generate a random string of specified size using given characters.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance, size_range=(30, 45)):
    """
    Generate a unique key for an instance. Assumes the instance has a 'key' field.
    """
    size = random.randint(*size_range)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_key_generator(instance)  # Regenerate if not unique
    return key


def unique_slug_generator(instance, new_slug=None):
    """
    Generate a unique slug for an instance. Assumes the instance has a 'slug' field
    and a 'title' field for initial slug generation.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f"{slug}-{random_string_generator(size=4)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


