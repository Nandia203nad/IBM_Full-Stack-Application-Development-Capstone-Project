# Uncomment the required imports before adding the code

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    if request.method == 'POST':  # Logout via POST for better CSRF protection
        logout(request)
        return JsonResponse(
            {"success": True, "message": "Logged out successfully"}
        )
    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=400
    )


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    # email_exist = False  # Remove unused variable
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except Exception:  # Use specific exception and remove unused whitespace
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username, first_name=first_name,
            last_name=last_name, password=password, email=email
        )
        # Login the user and redirect to the list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"username": username, "error": "Already Registered"}
        return JsonResponse(data)


# Method to get the list of cars
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append(
            {
                "CarModel": car_model.name,
                "CarMake": car_model.car_make.name
            }
        )
    return JsonResponse({"CarModels": cars})


# Method to get list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse(
        {"status": 200, "dealers": dealerships})


# Method to view reviews for individual dealer
def get_dealer_reviews(request, dealer_id):
    # If dealer id has been provided
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            # Call analyze_review_sentiments
            # check if the response is valid
            response = analyze_review_sentiments(
                review_detail['review'])
            print(response)

            if response is not None and 'sentiment' in response:
                review_detail['sentiment'] = response['sentiment']
            else:
                # If there's no sentiment, default to 'neutral'
                review_detail['sentiment'] = 'neutral'

        return JsonResponse({"status": 200, "reviews": reviews})

    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create an `add_review` view to submit a review
def add_review(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        print(data)  # Log the incoming data for debugging
        try:
            response = post_review(data)
            if response.get("status") == 200:
                print("Review posted successfully:", response)
            return JsonResponse(
                {
                    "status": 200,
                    "message": "Review posted successfully",
                    "review": data
                })
        except Exception as e:
            print(f"Error in posting review: {e}")
            return JsonResponse(
                {
                    "status": 401,
                    "message": "Error in posting review"
                })
    else:
        return JsonResponse(
            {
                "status": 403,
                "message": "Unauthorized"
            })
[
  {"id": 1, "city": "Topeka", "state": "Kansas", "address": "123 Innovation Way", "zip": "66601", "latitude": 39.0458, "longitude": -95.6812, "short_name": "Topeka Auto", "full_name": "Topeka Premium Car Dealership"},
  {"id": 2, "city": "Wichita", "state": "Kansas", "address": "456 Central Ave", "zip": "67202", "latitude": 37.6872, "longitude": -97.3301, "short_name": "Wichita Motors", "full_name": "Wichita Elite Auto Dealers"},
  {"id": 3, "city": "Overland Park", "state": "Kansas", "address": "789 Metcalf Ave", "zip": "66212", "latitude": 38.9822, "longitude": -94.6652, "short_name": "OP Car Center", "full_name": "Overland Park Car Center"},
  {"id": 4, "city": "Kansas City", "state": "Kansas", "address": "101 State Ave", "zip": "66102", "latitude": 39.1141, "longitude": -94.6275, "short_name": "KC Sales", "full_name": "Kansas City Auto Sales"},
  {"id": 5, "city": "Lawrence", "state": "Kansas", "address": "202 Iowa St", "zip": "66046", "latitude": 38.9717, "longitude": -95.2353, "short_name": "Jayhawk Motors", "full_name": "Lawrence Jayhawk Motors"},
  {"id": 6, "city": "Manhattan", "state": "Kansas", "address": "303 Tuttle Creek Blvd", "zip": "66502", "latitude": 39.1836, "longitude": -96.5717, "short_name": "Little Apple", "full_name": "Manhattan Little Apple Cars"},
  {"id": 7, "city": "Salina", "state": "Kansas", "address": "404 Ohio St", "zip": "67401", "latitude": 38.8403, "longitude": -97.6114, "short_name": "Salina Auto", "full_name": "Salina Certified Auto Group"},
  {"id": 8, "city": "Hutchinson", "state": "Kansas", "address": "505 Main St", "zip": "67501", "latitude": 38.0608, "longitude": -97.9298, "short_name": "Hutch Wheels", "full_name": "Hutchinson Quality Wheels"},
  {"id": 9, "city": "Olathe", "state": "Kansas", "address": "606 Santa Fe St", "zip": "66061", "latitude": 38.8814, "longitude": -94.8191, "short_name": "Olathe Ford", "full_name": "Olathe Premier Ford Sales"},
  {"id": 10, "city": "Dodge City", "state": "Kansas", "address": "707 Wyatt Earp Blvd", "zip": "67801", "latitude": 37.7528, "longitude": -100.0171, "short_name": "Cowboy Auto", "full_name": "Dodge City Cowboy Auto"},
  {"id": 11, "city": "Garden City", "state": "Kansas", "address": "808 Jones Ave", "zip": "67846", "latitude": 37.9717, "longitude": -100.8727, "short_name": "Garden Motors", "full_name": "Garden City Regional Motors"},
  {"id": 12, "city": "Emporia", "state": "Kansas", "address": "909 Commercial St", "zip": "66801", "latitude": 38.4039, "longitude": -96.1817, "short_name": "Emporia Auto", "full_name": "Emporia Community Auto"},
  {"id": 13, "city": "Pittsburg", "state": "Kansas", "address": "111 Broadway St", "zip": "66762", "latitude": 37.4109, "longitude": -94.7047, "short_name": "Pitt Vehicles", "full_name": "Pittsburg Family Vehicles"},
  {"id": 14, "city": "Atchison", "state": "Kansas", "address": "222 Commercial St", "zip": "66002", "latitude": 39.5631, "longitude": -95.1216, "short_name": "Riverfront", "full_name": "Atchison Riverfront Auto"},
  {"id": 15, "city": "Leavenworth", "state": "Kansas", "address": "333 4th St", "zip": "66048", "latitude": 39.3111, "longitude": -94.9225, "short_name": "Pioneer Auto", "full_name": "Leavenworth Pioneer Auto"},
  {"id": 16, "city": "Junction City", "state": "Kansas", "address": "444 Washington St", "zip": "66441", "latitude": 39.0286, "longitude": -96.8314, "short_name": "Flint Hills", "full_name": "Junction City Flint Hills Auto"},
  {"id": 17, "city": "Hayes", "state": "Kansas", "address": "555 Vine St", "zip": "67601", "latitude": 38.8794, "longitude": -99.3268, "short_name": "Hays Car Co", "full_name": "Hays Enterprise Car Company"},
  {"id": 18, "city": "Liberal", "state": "Kansas", "address": "666 Kansas Ave", "zip": "67901", "latitude": 37.0431, "longitude": -100.9201, "short_name": "Southwest", "full_name": "Liberal Southwest Auto Traders"},
  {"id": 19, "city": "Great Bend", "state": "Kansas", "address": "777 10th St", "zip": "67530", "latitude": 38.3645, "longitude": -98.7648, "short_name": "Prairie Auto", "full_name": "Great Bend Prairie Auto"},
  {"id": 20, "city": "McPherson", "state": "Kansas", "address": "888 Main St", "zip": "67460", "latitude": 38.3708, "longitude": -97.6642, "short_name": "McPherson Car", "full_name": "McPherson Quality Car Care"},
  {"id": 21, "city": "Ottawa", "state": "Kansas", "address": "999 Princeton St", "zip": "66067", "latitude": 38.6158, "longitude": -95.2686, "short_name": "Ottawa Direct", "full_name": "Ottawa Direct Auto Sales"},
  {"id": 22, "city": "Newton", "state": "Kansas", "address": "124 Main St", "zip": "67114", "latitude": 38.0442, "longitude": -97.3456, "short_name": "Newton Motors", "full_name": "Newton Family Motors"},
  {"id": 23, "city": "El Dorado", "state": "Kansas", "address": "235 Central Ave", "zip": "67042", "latitude": 37.8172, "longitude": -96.8606, "short_name": "Oil Hill Auto", "full_name": "El Dorado Oil Hill Auto"},
  {"id": 24, "city": "Winfield", "state": "Kansas", "address": "346 Main St", "zip": "67156", "latitude": 37.2411, "longitude": -96.9964, "short_name": "Winfield Auto", "full_name": "Winfield Direct Auto"},
  {"id": 25, "city": "Arkansas City", "state": "Kansas", "address": "457 Summit St", "zip": "67005", "latitude": 37.0617, "longitude": -97.0384, "short_name": "Ark City Cars", "full_name": "Arkansas City Car Brokers"},
  {"id": 26, "city": "Wellington", "state": "Kansas", "address": "568 G St", "zip": "67152", "latitude": 37.2656, "longitude": -97.4003, "short_name": "Wheat City", "full_name": "Wellington Wheat City Autos"},
  {"id": 27, "city": "Parsons", "state": "Kansas", "address": "679 Main St", "zip": "67357", "latitude": 37.3403, "longitude": -95.2614, "short_name": "Parsons Auto", "full_name": "Parsons Local Auto Sales"},
  {"id": 28, "city": "Coffeyville", "state": "Kansas", "address": "790 11th St", "zip": "67337", "latitude": 37.0378, "longitude": -95.6164, "short_name": "Red Raven", "full_name": "Coffeyville Red Raven Motors"},
  {"id": 29, "city": "Independence", "state": "Kansas", "address": "901 Penn Ave", "zip": "67301", "latitude": 37.2242, "longitude": -95.7083, "short_name": "Indy Wheels", "full_name": "Independence Indy Wheels"},
  {"id": 30, "city": "Chanute", "state": "Kansas", "address": "135 Santa Fe Ave", "zip": "66720", "latitude": 37.6792, "longitude": -95.4544, "short_name": "Chanute Auto", "full_name": "Chanute Certified Vehicles"},
  {"id": 31, "city": "Fort Scott", "state": "Kansas", "address": "246 National Ave", "zip": "66701", "latitude": 37.8398, "longitude": -94.7083, "short_name": "Historic Fort", "full_name": "Fort Scott Historic Auto"},
  {"id": 32, "city": "Iola", "state": "Kansas", "address": "357 State St", "zip": "66749", "latitude": 37.9245, "longitude": -95.4011, "short_name": "Iola Car Co", "full_name": "Iola Local Car Company"},
  {"id": 33, "city": "Pratt", "state": "Kansas", "address": "468 First St", "zip": "67124", "latitude": 37.6439, "longitude": -98.7376, "short_name": "Pratt Green", "full_name": "Pratt Green Light Motors"},
  {"id": 34, "city": "Abilene", "state": "Kansas", "address": "579 Buckeye Ave", "zip": "67410", "latitude": 38.9172, "longitude": -97.2136, "short_name": "Eisenhower", "full_name": "Abilene Eisenhower Auto"},
  {"id": 35, "city": "Colby", "state": "Kansas", "address": "690 Range Ave", "zip": "67701", "latitude": 39.3958, "longitude": -101.0524, "short_name": "Colby Express", "full_name": "Colby Express Auto Sales"},
  {"id": 36, "city": "Goodland", "state": "Kansas", "address": "801 Main St", "zip": "67735", "latitude": 39.3494, "longitude": -101.7110, "short_name": "Borderline", "full_name": "Goodland Borderline Cars"},
  {"id": 37, "city": "Russell", "state": "Kansas", "address": "912 Fossil St", "zip": "67665", "latitude": 38.8922, "longitude": -98.8573, "short_name": "Fossil Creek", "full_name": "Russell Fossil Creek Auto"},
  {"id": 38, "city": "Concordia", "state": "Kansas", "address": "147 Lincoln St", "zip": "66901", "latitude": 39.5708, "longitude": -97.6589, "short_name": "Concordia Car", "full_name": "Concordia Elite Car Sales"},
  {"id": 39, "city": "Beloit", "state": "Kansas", "address": "258 South St", "zip": "67420", "latitude": 39.4622, "longitude": -98.1092, "short_name": "Beloit Sales", "full_name": "Beloit Auto Marketing"},
  {"id": 40, "city": "Clay Center", "state": "Kansas", "address": "369 5th St", "zip": "67432", "latitude": 39.3775, "longitude": -97.1264, "short_name": "Clay Center", "full_name": "Clay Center Automotive Group"},
  {"id": 41, "city": "Marysville", "state": "Kansas", "address": "480 Broadway", "zip": "66508", "latitude": 39.8417, "longitude": -96.6508, "short_name": "Pony Express", "full_name": "Marysville Pony Express Auto"},
  {"id": 42, "city": "Hiawatha", "state": "Kansas", "address": "591 Oregon St", "zip": "66434", "latitude": 39.8525, "longitude": -95.5342, "short_name": "Hiawatha Car", "full_name": "Hiawatha Premier Car Care"},
  {"id": 43, "city": "Paola", "state": "Kansas", "address": "702 Silver St", "zip": "66071", "latitude": 38.5728, "longitude": -94.8789, "short_name": "Paola Choice", "full_name": "Paola Choice Pre-Owned"},
  {"id": 44, "city": "Louisburg", "state": "Kansas", "address": "813 Amity St", "zip": "66053", "latitude": 38.6192, "longitude": -94.6789, "short_name": "Louisburg Jet", "full_name": "Louisburg Jet Auto Sales"},
  {"id": 45, "city": "Gardner", "state": "Kansas", "address": "924 Main St", "zip": "66030", "latitude": 38.8108, "longitude": -94.9269, "short_name": "Gardner Auto", "full_name": "Gardner Hometown Auto Group"},
  {"id": 46, "city": "Spring Hill", "state": "Kansas", "address": "158 Webster St", "zip": "66083", "latitude": 38.7425, "longitude": -94.8261, "short_name": "Spring Hill", "full_name": "Spring Hill National Auto"},
  {"id": 47, "city": "Lansing", "state": "Kansas", "address": "269 Main St", "zip": "66043", "latitude": 39.2489, "longitude": -94.8911, "short_name": "Lansing Auto", "full_name": "Lansing Authorized Sales"},
  {"id": 48, "city": "Bonner Springs", "state": "Kansas", "address": "380 Front St", "zip": "66012", "latitude": 39.0600, "longitude": -94.8819, "short_name": "Bonner Auto", "full_name": "Bonner Springs Auto Exchange"},
  {"id": 49, "city": "Roeland Park", "state": "Kansas", "address": "491 Roe Ave", "zip": "66205", "latitude": 39.0345, "longitude": -94.6394, "short_name": "Roe Motors", "full_name": "Roeland Park Roe Motors"},
  {"id": 50, "city": "Fairway", "state": "Kansas", "address": "502 Shawnee Mission Pkwy", "zip": "66205", "latitude": 39.0222, "longitude": -94.6294, "short_name": "Fairway Elite", "full_name": "Fairway Elite Automobile Gallery"}
]
]
