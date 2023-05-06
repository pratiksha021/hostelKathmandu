from django import forms
from django.contrib.auth.models import User
from . import models



class CustomerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields=['address','mobile','profile_pic','email','dob','gender']

class HostelForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model=models.Hostel
        fields=['name','description','price','location','address','contact','email','images','images2','images3','images4','rating','num_rating','wifi_choice','canteen_choice','parking_choice','hotwater_choice']

class roomForm(forms.ModelForm):
    class Meta:
        model=models.Room
        fields=['hostel','type_name','occupancy','room_type','maximum','available','cost','img1','img2','img3']


#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class BookingForm(forms.ModelForm):
    class Meta:
        model=models.Booking
        fields=[]

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name', 'id':'name','name':'name'}))
    Email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email', 'id':'email', 'name':'email'}))
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 5, 'name':'message', 'class':'form-control','placeholder':'Message'}))
