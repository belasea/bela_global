from django.db import models


class OurBackground(models.Model):
    title = models.CharField(
        max_length=200, 
        default="Our Background",
        help_text="The main heading of the section."
    )
    
    # Using TextField for the paragraphs to allow for longer content
    intro_paragraph = models.TextField(
        help_text="The first paragraph (emphasized with the side border in the UI)."
    )
    history_paragraph = models.TextField(
        help_text="The second paragraph detailing the evolution of the company."
    )
    mission_statement = models.TextField(
        help_text="The final summary/vision statement at the bottom."
    )
    
    # Badge and Image data
    years_experience = models.PositiveIntegerField(
        default=5,
        help_text="The number to display in the teal experience badge."
    )
    featured_image = models.ImageField(
        upload_to='background/',
        help_text="The main image showing the consultation/office setting.",
        blank=True, null=True
    )
    

    def __str__(self):
        return self.title
    

class OurGoal(models.Model):
    # Define choices
    GOAL_CHOICES = [
        ('mission', 'Mission'),
        ('vision', 'Vision'),
        ('events', 'Events'),
    ]

    title = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        unique=True
    )
    message = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)   # controls display order
    is_active = models.BooleanField(default=True)    # toggle visibility

    class Meta:
        ordering = ['order']  # ensures items show in order

    def __str__(self):
        return self.get_title_display()
    

class Facility(models.Model):
    # Define choices
    FACILITY_CHOICES = [
        ('one_to_one', 'One to One Session'),
        ('assessment', 'Assessment of documentation'),
        ('check_verify', 'Documents check and verify'),
        ('information', 'Information Pack'),
        ('event', 'Even Participation'),
        ('online_portal', 'Online Portal'),
    ]

    name = models.CharField(
        max_length=50,
        choices=FACILITY_CHOICES,
        unique=True
    )
    description = models.TextField(blank=True, null=True)  # optional description
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()  # shows human-readable choice
