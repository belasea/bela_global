from django.db import models

class Slider(models.Model):
    label = models.CharField(max_length=50, help_text="e.g., 'New' or 'Essentials'")
    title = models.CharField(max_length=200)
    subtitle = models.TextField()
    image = models.ImageField(upload_to='sliders/')
    link_url = models.CharField(max_length=500, default="#", help_text="URL for the Learn More button")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class SkincareSection(models.Model):
    title = models.CharField(max_length=100, help_text="Internal name for this entry")

    # Left Column Images
    # Left Column Images
    left_img_a = models.ImageField(
        upload_to='skincare/', 
        verbose_name="Left Image A",
        help_text="Required dimensions: 320x392px"
    )
    left_img_b = models.ImageField(
        upload_to='skincare/', 
        verbose_name="Left Image B",
        help_text="Required dimensions: 320x392px"
    )

    # Center Column Content
    center_label = models.CharField(max_length=50, default="Efficiency")
    center_title_a = models.CharField(max_length=200, verbose_name="Center Title A")
    center_title_b = models.CharField(max_length=200, verbose_name="Center Title B")
    
    # Right Column Overlapping Images
    right_top_img_a = models.ImageField(
        upload_to='skincare/', 
        verbose_name="Right Top A",
        help_text="Required dimensions: 250x245px"
    )
    right_top_img_b = models.ImageField(upload_to='skincare/', 
        verbose_name="Right Top B" ,
        help_text="Required dimensions: 250x245px"
    )
    
    right_bottom_img_a = models.ImageField(
        upload_to='skincare/', 
        verbose_name="Right Bottom A",
        help_text="Required dimensions: 250x245px"
    )
    right_bottom_img_b = models.ImageField(
        upload_to='skincare/', 
        verbose_name="Right Bottom B",
        help_text="Required dimensions: 250x245px"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title