import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
           response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs) 
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = response.json()
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        dealers = json_result
        if type(dealers) == str:
            dealers = json.loads(dealers)
        # For each dealer object
        for dealer in dealers:
            print("DEALER CONTENT -----------------")
            print(dealer)
            # Create a CarDealer object with values
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id_from_cf(url, id):
    #TODO Start from here
    json_result = get_request(url, **{"dealer_id" : id})
    if json_result:
        dealers = json_result
        if type(dealers) == str:
            dealers = json.loads(dealers)
        # Create a CarDealer object with values
        dealer = dealers[0]
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                               short_name=dealer["short_name"],
                               st=dealer["st"], zip=dealer["zip"])

    return dealer_obj

def get_dealer_by_state_from_cf(url, state):
    json_result = get_request(url, **{"state" : state})
    if json_result:
        dealers = json_result
        if type(dealers) == str:
            dealers = json.loads(dealers)
        results = []
        # For each dealer object
        for dealer in dealers:
            print("DEALER CONTENT -----------------")
            print(dealer)
            # Create a CarDealer object with values
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
        return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
'''
def get_dealer_reviews_from_cf(url):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = response.json()
    return json_data
'''
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print("POST to {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=payload)
    except:
        print("Network issue")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = response.json()
    return json_data


def get_dealers_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, **{"dealerID":dealer_id})
    if json_result:
        reviews = json_result
        if type(reviews) == str:
            reviews = json.loads(reviews)
        for review in reviews:
            print("REVIEW CONTENT -----------------")
            print(review)
            # Create a DealerReview object with values
            review_obj = DealerReview(**review)
            review_obj.sentiment = analyze_review_sentiments(review['review'])
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    try:
        url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/a14d230c-6299-42fe-a397-9eca7bf3bb8c"
        api_key = "YjUhQkiDsAY7Iv0FRkLHdWEl9Br9vy_89V0v8JH014tk"
        authenticator = IAMAuthenticator(api_key) 
        natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
        natural_language_understanding.set_service_url(url) 
        response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result() 
        label=json.dumps(response, indent=2) 
        label = response['sentiment']['document']['label'] 
        print("NLU SUCCESS ------------") 
        return label
    except Exception as e:
        print("NLU FAILURE ------------")
        print(e)
        return "No sentiment"

