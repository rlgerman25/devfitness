from django.db import models
from django.contrib.auth.models import User

class FitnessPlan(models.Model):
    title = models.CharField(max_length= 255)
    text = models.TextField()
    image = models.ImageField(upload_to='plans/images/', blank=True)
    image_credit = models.CharField(max_length=300, blank=True)
    video = models.CharField(max_length= 250, blank=True)
    video_credit = models.CharField(max_length=300, blank=True)
    date = models.DateField()
    premium = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    stripeid = models.CharField(max_length= 255)
    stripe_subscription = models.CharField(max_length= 255)
    cancel_at_period_end = models.BooleanField(default= False)
    membership = models.BooleanField(default= False)

    def __str__(self):
        return str(self.user)