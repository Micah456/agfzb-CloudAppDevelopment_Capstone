from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_by_state_from_cf, get_dealers_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .models import CarMake, CarModel
from datetime import datetime

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request,'djangoapp/login.html')
    else:
        return render(request,'djangoapp/login.html')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)


    


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/20c90a8b-c798-46b7-b609-061b69cda4c8/dealership-package/get-dealership"
        state = request.GET.get('state')
        dealerships = []
        if state:
            print(state + "-------------------------------")
            dealerships = get_dealer_by_state_from_cf(url, state)
        else:
            # Get dealers from the URL
            dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealerships'] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/20c90a8b-c798-46b7-b609-061b69cda4c8/dealership-package/get-review"
    print(str(dealer_id) + "-------------------------------")
    reviews = get_dealers_reviews_from_cf(url, dealer_id)
    #review_names = ', '.join([review.name + " - Sentiment: " + review.sentiment for review in reviews])
    context['reviews'] = reviews
    context['dealer_id'] = dealer_id
    return render(request, 'djangoapp/dealer_details.html', context)

def get_dealership_from_id(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/20c90a8b-c798-46b7-b609-061b69cda4c8/dealership-package/get-dealership"
        # Get dealers from the URL
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        # Return a list of dealer short name
        return HttpResponse(dealer.short_name)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            review = dict()
            review["name"] = user.first_name + " " + user.last_name
            review["time"] = datetime.utcnow().isoformat()
            review["dealership"] = int(dealer_id)
            review["review"] = request.POST['review-content']
            review["id"] = int(datetime.utcnow().strftime("%y%-m%-d%-H%-M%-S"))
            if request.POST.get('has-purchased', False):
                review["purchase"] = True
                review["purchase_date"] = datetime.strptime(request.POST['purchase-date'], "%Y-%m-%d").strftime("%m/%d/%Y")
                car_details = request.POST['car-select'].split("-")
                review["car_make"] = car_details[1]
                review["car_model"] = car_details[0]
                review["car_year"] = car_details[2]
                #2023-06-06T15:28:29.731314 #"%Y-%m-%dT%H:%M:%S:%f"
            else:
                review["purchase"] = False
            json_payload = dict()
            json_payload['review'] = review
            url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/20c90a8b-c798-46b7-b609-061b69cda4c8/dealership-package/post-review"
            print(json_payload)
            response = post_request(url=url, json_payload=json_payload)
            #print(response)
            redirect("djangoapp:dealer_details", dealer_id=dealer_id)

    else:
        context = {}
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/20c90a8b-c798-46b7-b609-061b69cda4c8/dealership-package/get-dealership"
        # Get dealers from the URL
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        #cars = CarMake.objects.all()
        #cars = cars[0].carmodel_set.all()
        context['dealer'] = dealer
        context['cars'] = cars
        return render(request,'djangoapp/add_review.html', context)