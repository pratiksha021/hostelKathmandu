from django.shortcuts import render,redirect,reverse, get_object_or_404
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from .models import Hostel

def home_view(request):
    hostels=models.Hostel.objects.all()
    if 'hostel_ids' in request.COOKIES:
        hostel_ids = request.COOKIES['hostel_ids']
        counter=hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:
        Hostel_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'hostels':hostels,'Hostel_count_in_cart':Hostel_count_in_cart})


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

def hostel_detail(request, id):
    hostel=models.Hostel.objects.get(id=id)
    data = {
        'hostel':hostel
    }
    return render(request, 'ecom/hostel_detail.html', data)



#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    hostelcount=models.Hostel.objects.all().count()
    bookingcount=models.Booking.objects.all().count()

    # for recent booking tables
    Booking=models.Booking.objects.all()
    bookinged_Hostels=[]
    bookinged_bys=[]
    for booking in Booking:
        bookinged_Hostel=models.Hostel.objects.all().filter(id=booking.Hostel.id)
        bookinged_by=models.Customer.objects.all().filter(id = booking.customer.id)
        bookinged_Hostels.append(bookinged_Hostel)
        bookinged_bys.append(bookinged_by)

    mydict={
    'customercount':customercount,
    'hostelcount':hostelcount,
    'bookingcount':bookingcount,
    'data':zip(bookinged_Hostels,bookinged_bys,Booking),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)

# admin view the Hostel
@login_required(login_url='adminlogin')
def admin_Hostels_view(request):
    Hostels=models.Hostel.objects.all()
    return render(request,'ecom/admin_hostels.html',{'Hostels':Hostels})


# admin add Hostel by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_Hostel_view(request):
    HostelForm=forms.HostelForm()
    if request.method=='POST':
        HostelForm=forms.HostelForm(request.POST, request.FILES)
        if HostelForm.is_valid():
            HostelForm.save()
        return HttpResponseRedirect('admin-hostels')
    return render(request,'ecom/admin_add_hostels.html',{'HostelForm':HostelForm})


@login_required(login_url='adminlogin')
def delete_Hostel_view(request,pk):
    Hostel=models.Hostel.objects.get(id=pk)
    Hostel.delete()
    return redirect('admin-hostels')


@login_required(login_url='adminlogin')
def update_Hostel_view(request,pk):
    Hostel=models.Hostel.objects.get(id=pk)
    HostelForm=forms.HostelForm(instance=Hostel)
    if request.method=='POST':
        HostelForm=forms.HostelForm(request.POST,request.FILES,instance=Hostel)
        if HostelForm.is_valid():
            HostelForm.save()
            return redirect('admin-hostels')
    return render(request,'ecom/admin_update_Hostel.html',{'HostelForm':HostelForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    Booking=models.Booking.objects.all()
    bookinged_Hostels=[]
    bookinged_bys=[]
    for booking in Booking:
        bookinged_Hostel=models.Hostel.objects.all().filter(id=booking.Hostel.id)
        bookinged_by=models.Customer.objects.all().filter(id = booking.customer.id)
        bookinged_Hostels.append(bookinged_Hostel)
        bookinged_bys.append(bookinged_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(bookinged_Hostels,bookinged_bys,Booking)})


@login_required(login_url='adminlogin')
def delete_booking_view(request,pk):
    booking=models.Booking.objects.get(id=pk)
    booking.delete()
    return redirect('admin-view-booking')

# for changing status of booking (pending,delivered...)
@login_required(login_url='adminlogin')
def update_booking_view(request,pk):
    booking=models.Booking.objects.get(id=pk)
    bookingForm=forms.bookingForm(instance=booking)
    if request.method=='POST':
        bookingForm=forms.bookingForm(request.POST,instance=booking)
        if bookingForm.is_valid():
            bookingForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_booking.html',{'bookingForm':bookingForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().booking_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    hostels=models.Hostel.objects.all().filter(name__icontains=query)
    if 'hostel_ids' in request.COOKIES:
        hostel_ids = request.COOKIES['hostel_ids']
        counter=hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:
        Hostel_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'hostels':hostels,'word':word,'Hostel_count_in_cart':Hostel_count_in_cart})
    return render(request,'ecom/index.html',{'hostels':hostels,'word':word,'Hostel_count_in_cart':Hostel_count_in_cart})


# any one can add Hostel to cart, no need of signin
def add_to_cart_view(request,pk):   
    hostels=models.Hostel.objects.all()

    #for cart counter, fetching Hostels ids added by customer from cookies
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        counter=Hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:   
        Hostel_count_in_cart=1

    response = render(request, 'ecom/index.html',{'hostels':hostels,'Hostel_count_in_cart':Hostel_count_in_cart})

    #adding Hostel id to cookies
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        if Hostel_ids=="":
            Hostel_ids=str(pk)
        else:
            Hostel_ids=Hostel_ids+"|"+str(pk)
        response.set_cookie('Hostel_ids', Hostel_ids)
    else:
        response.set_cookie('Hostel_ids', pk)

    Hostel=models.Hostel.objects.get(id=pk)
    messages.info(request, Hostel.name + ' added to cart successfully!')

    return response



# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        counter=Hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:
        Hostel_count_in_cart=0

    # fetching Hostel details from db whose id is present in cookie
    Hostels=None
    total=0
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        if Hostel_ids != "":
            Hostel_id_in_cart=Hostel_ids.split('|')
            Hostels=models.Hostel.objects.all().filter(id__in = Hostel_id_in_cart)

            #for total price shown in cart
            for p in Hostels:
                total=total+p.price
    return render(request,'ecom/cart.html',{'Hostels':Hostels,'total':total,'Hostel_count_in_cart':Hostel_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        counter=Hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:
        Hostel_count_in_cart=0

    # removing Hostel id from cookie
    total=0
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        Hostel_id_in_cart=Hostel_ids.split('|')
        Hostel_id_in_cart=list(set(Hostel_id_in_cart))
        Hostel_id_in_cart.remove(str(pk))
        Hostels=models.Hostel.objects.all().filter(id__in = Hostel_id_in_cart)
        #for total price shown in cart after removing Hostel
        for p in Hostels:
            total=total+p.price

        #  for update coookie value after removing Hostel id in cart
        value=""
        for i in range(len(Hostel_id_in_cart)):
            if i==0:
                value=value+Hostel_id_in_cart[0]
            else:
                value=value+"|"+Hostel_id_in_cart[i]
        response = render(request, 'ecom/cart.html',{'Hostels':Hostels,'total':total,'Hostel_count_in_cart':Hostel_count_in_cart})
        if value=="":
            response.delete_cookie('Hostel_ids')
        response.set_cookie('Hostel_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    Hostels=models.Hostel.objects.all()
    print("hiii")
   
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        counter=Hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
        
    else:
        Hostel_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'Hostels':Hostels,'Hostel_count_in_cart':Hostel_count_in_cart})



# shipment address before placing booking
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether Hostel is present in cart or not
    # if there is no Hostel in cart we will not show address form
    Hostel_in_cart=False
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        if Hostel_ids != "":
            Hostel_in_cart=True
    #for counter in cart
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        counter=Hostel_ids.split('|')
        Hostel_count_in_cart=len(set(counter))
    else:
        Hostel_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of booking placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of Hostel from db
            total=0
            if 'Hostel_ids' in request.COOKIES:
                Hostel_ids = request.COOKIES['Hostel_ids']
                if Hostel_ids != "":
                    Hostel_id_in_cart=Hostel_ids.split('|')
                    Hostels=models.Hostel.objects.all().filter(id__in = Hostel_id_in_cart)
                    for p in Hostels:
                        total=total+p.price

            response = render(request, 'ecom/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'ecom/customer_address.html',{'addressForm':addressForm,'Hostel_in_cart':Hostel_in_cart,'Hostel_count_in_cart':Hostel_count_in_cart})




# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place booking | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch Hostel id from cookies then respective details from db
    # then we will create booking objects and store in db
    # after that we will delete cookies because after booking placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    Hostels=None
    email=None
    mobile=None
    address=None
    if 'Hostel_ids' in request.COOKIES:
        Hostel_ids = request.COOKIES['Hostel_ids']
        if Hostel_ids != "":
            Hostel_id_in_cart=Hostel_ids.split('|')
            Hostels=models.Hostel.objects.all().filter(id__in = Hostel_id_in_cart)
            # Here we get Hostels list that will be bookinged by one customer at a time

    # these things can be change so accessing at the time of booking...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of Booking as much there is a Hostels
    # suppose if we have 5 items in cart and we place booking....so 5 rows will be created in Booking table
    # there will be lot of redundant data in Booking table...but its become more complicated if we normalize it
    for Hostel in Hostels:
        models.Booking.objects.get_or_create(customer=customer,Hostel=Hostel,status='Pending',email=email,mobile=mobile,address=address)

    # after booking placed cookies should be deleted
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('Hostel_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response




@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_booking_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    Booking=models.Booking.objects.all().filter(customer_id = customer)
    bookinged_Hostels=[]
    for booking in Booking:
        bookinged_Hostel=models.Hostel.objects.all().filter(id=booking.Hostel.id)
        bookinged_Hostels.append(bookinged_Hostel)

    return render(request,'ecom/my_booking.html',{'data':zip(bookinged_Hostels,Booking)})




#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,bookingID,HostelID):
    booking=models.Booking.objects.get(id=bookingID)
    Hostel=models.Hostel.objects.get(id=HostelID)
    mydict={
        'bookingDate':booking.booking_date,
        'customerName':request.user,
        'customerEmail':booking.email,
        'customerMobile':booking.mobile,
        'shipmentAddress':booking.address,
        'Bookingtatus':booking.status,

        'HostelName':Hostel.name,
        'HostelImage':Hostel.Hostel_image,
        'HostelPrice':Hostel.price,
        'HostelDescription':Hostel.description,


    }
    return render_to_pdf('ecom/download_invoice.html',mydict)






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})
