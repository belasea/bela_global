import random
import string
from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    """Generates a random string of fixed size."""
    return ''.join(random.choice(chars) for _ in range(size))

def unique_slug_generator(instance, new_slug=None):
    """
    Generates a unique slug for a model instance.
    It assumes the instance has a 'title' or 'name' field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        # Check for 'title', fallback to 'name', then fallback to 'id'
        if hasattr(instance, 'title') and instance.title:
            slug = slugify(instance.title)
        elif hasattr(instance, 'name') and instance.name:
            slug = slugify(instance.name)
        else:
            slug = "item-" + random_string_generator(size=4)

    Klass = instance.__class__
    # Check if the generated slug already exists in this model
    qs_exists = Klass.objects.filter(slug=slug).exists()
    
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        # Recursively call the function until a unique slug is found
        return unique_slug_generator(instance, new_slug=new_slug)
    
    return slug