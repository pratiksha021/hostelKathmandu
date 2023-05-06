from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.mail import EmailMessage
from hostel.emails import BOOKING_EMAIL



# Create your models here.
class Hostel(models.Model):
    WIFI_CHOICES = [
        ("5G network", "5G network"),
        ("Not Available", "Not Available"),
    ]

    CANTEEN_CHOICES = [
        ("Available", "Available"),
        ("Not Available", "Not Available"),
    ]

    PARKING_CHOICES = [
        ("Available", "Available"),
        ("Not Available", "Not Available"),
    ]

    HOTWATER_CHOICES = [
        ("Available", "Available"),
        ("Not Available", "Not Available"),
    ]

    LOCATION_CHOICES = [
        ("Kathmandu", "Kathmandu"),
        ("Lalitpur", "Lalitpur"),
        ("Bhaktapur", "Bhaktapur"),
    ]

    name = models.CharField(max_length=100)
    images = models.ImageField(upload_to='hostel_image/img1/',null=True,blank=True)
    images2 = models.ImageField(upload_to='hostel_image/img2/',null=True,blank=True)
    images3 = models.ImageField(upload_to='hostel_image/img3/',null=True,blank=True)
    images4 = models.ImageField(upload_to='hostel_image/img4/',null=True,blank=True)

    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2) 
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES,default="Kathmandu")
    address = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, default='email')
    rating = models.DecimalField(decimal_places=2, max_digits=4, default=3)
    num_rating = models.PositiveIntegerField(default=0)
    wifi_choice = models.CharField(max_length=100, choices=WIFI_CHOICES, default="5G network")
    canteen_choice = models.CharField(max_length=100, choices=CANTEEN_CHOICES,default="Available")
    parking_choice = models.CharField(max_length=100, choices=PARKING_CHOICES,default="Available")
    hotwater_choice = models.CharField(max_length=100, choices=HOTWATER_CHOICES,default="Available")    

    # owner = models.ForeignKey(HostelOwner, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
            # Override the slug field with a slugified version of the name field
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)

# class Image(models.Model):
#     image = models.ImageField(upload_to='hostel_image/',null=True,blank=True)

class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/CustomerProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    email = models.EmailField(max_length=100)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ), blank=True)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name



class Manager(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)

    def __str__(self):
        """Unicode representation of Manager."""
        return self.user.username



class Room(models.Model):
   
    OCCUPANCY_CHOICES = [
        ("SINGLE", "SINGLE"),
        ("DOUBLE", "DOUBLE"),
    ]
    TYPE_CHOICES = [
        ("A/C(Air Conditioned)", "A/C(Air Conditioned)"),
        ("Non A/C(Non Air Conditioned)", "Non A/C(Non Air Conditioned)"),
    ]

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=100, default="Deluxe")
    occupancy = models.CharField(max_length=50, choices=OCCUPANCY_CHOICES , default="SINGLE")
    room_type = models.CharField(max_length=50, choices=TYPE_CHOICES , default="Non A/C(Non Air Conditioned)")
    maximum = models.PositiveIntegerField(default=10)
    available = models.PositiveIntegerField(default=10)
    cost = models.PositiveIntegerField(default=10000)
    img1= models.ImageField(upload_to='room_image/img1',null=True,blank=True)
    img2= models.ImageField(upload_to='room_image/img2',null=True,blank=True)
    img3 = models.ImageField(upload_to='room_image/img3',null=True,blank=True)

    def get_absolute_url(self):
        """Return absolute url for Room."""
        return reverse('hotels:room-detail', args=[str(self.hostel.pk), str(self.pk)])

    def __str__(self):
        """Unicode representation of Room."""
        return str(self.hostel) + ' ' + self.type_name + ' ' + self.occupancy + ' ' + self.room_type

class Transaction(models.Model):
    """Model definition for Transaction."""
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_hotel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.PositiveIntegerField()
    reason = models.CharField(max_length=100)
    success = models.BooleanField(default=False)

    def send_email(self, transaction):
        try:
            subject = "Invoice for Transaction %d" % transaction.id
            body = BOOKING_EMAIL % (transaction.from_user.username, transaction.id, transaction.from_user.username, transaction.to_hotel, transaction.amount, transaction.time, transaction.success)
            email = EmailMessage(subject, body, to=[transaction.from_user.email])
            email.send()
        except Exception as e:
            print("%s\nUnable to send email to %s" % (e, transaction.from_user.email))

    @transaction.atomic
    def make_transaction(self,from_user, to_hotel, amount, reason):
        status = False
        if from_user.wallet >= amount:
            from_user.wallet -= amount
            to_hotel.wallet += amount
            from_user.save()
            to_hotel.save()
            status = True
        transaction = Transaction(from_user=from_user.user, to_hotel=to_hotel, amount=amount, success=status, reason=reason)
        transaction.save()
        self.send_email(transaction)
        return transaction, status


    def __str__(self):
        """Unicode representation of Transaction."""
        return str(self.id) + ': ' + str(self.from_user) + ' to ' + str(self.to_hotel) + ' - ' + str(self.amount)


class Booking(models.Model):
    """Model definition for Booking."""
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    num_rooms = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    user_rating = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Unicode representation of Booking."""
        return str(self.room.pk) + ' ' + str(self.num_rooms)




class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name
