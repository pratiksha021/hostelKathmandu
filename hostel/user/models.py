from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name

class HostelOwner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

class Hostel(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    hostel_image= models.ImageField(upload_to='product_image/',null=True,blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField()
    rating = models.FloatField()
    has_wifi = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)
    has_lounge = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    # owner = models.ForeignKey(HostelOwner, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
            # Override the slug field with a slugified version of the name field
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)



class Booking(models.Model):
    STATUS =(
        ('Pending','Pending'),
        ('Booking Confirmed','Booking Confirmed'),
        ('Out for Use','Out for Use'),
        ('Used','Used'),
    )
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    hostel =models.ForeignKey('Hostel',on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=50,null=True)
    address = models.CharField(max_length=500,null=True)
    mobile = models.CharField(max_length=20,null=True)
    booking_date= models.DateField(auto_now_add=True,null=True)
    status=models.CharField(max_length=50,null=True,choices=STATUS)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
