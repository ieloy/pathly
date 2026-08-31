import json
import os
import random
import requests
import xml.etree.ElementTree as ET
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from google.maps import routing_v2

from .models import User, Groupsaves


# Create your views here.
@login_required
def index(request):
    places = get_places(request)
    message = ""

    if not places:
      message = "Make sure to upload your kml file first!"

    return render(request, "pathly/index.html", {
      "places": places,
      "message": message
    })

def register(request):
  if request.method == "POST":
    username = request.POST["username"]
    password = request.POST["password"]
    confirm_password = request.POST["confirm_password"]

    if password != confirm_password:
      print("no matcho")
      return render(request, "pathly/register.html", {
        "message": "Passwords must match"
      })
    
    # model veranderen in de database
    try:
      user = User.objects.create_user(
        username=username, 
        password=password
        )
      
    except IntegrityError:
      print("something went wrong")
      return render(request, "pathly/register.html", {
        "message": "Username already taken!"
      })

    user = authenticate(
      request,
      username=username,
      password=password
    )

    if user is not None:
      login(request, user)
    else:
      return render(request, "pathly/register.html", {
        "message": "Something went wrong, try again."
      })

    return redirect("index")
  
  else:
    return render(request, "pathly/register.html")

def login_view(request):
  if request.method == "POST":
    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(
      request,
      username=username,
      password=password
    )

    if user is not None:
      login(request, user)
      return redirect("index")
    else:
      return render(request, "pathly/login_view.html", {
        "message": "Something went wrong"
      })
    
  else:
    return render(request, "pathly/login_view.html")

@login_required
def mapinfo(request):
    places = request.session.get("places_extra_info")

    if not places:
      return redirect("index")

    return render(request, "pathly/mapinfo.html", {
      "places": places
    })

@login_required
def routes(request):
    groups = request.session.get("sorted_groups")
    places = request.session.get("places")

    if not groups or not places:
      saved_groups = Groupsaves.objects.filter(
        user=request.user
      ).order_by("-created_at").first()

      if saved_groups and saved_groups.places:
        groups = saved_groups.groups
        places = saved_groups.places

        request.session["sorted_groups"] = groups
        request.session["places"] = places
      else:
        messages.error(request, "Make sure to sort your locations first!")
        return redirect("sorting")
    
    locations_by_id = get_locations_by_id(places)
    api_key = get_credentials()

    sorted_groups = {}

    for index, (group_key, location_ids) in enumerate(groups.items(), start=1):
      location_list = []

      for location_id in location_ids:
        location_list.append(
          locations_by_id[int(location_id)]
        )
      
      sorted_groups[group_key] = {
        "name": f"Group {index}",
        "locations": location_list,
      }

    return render(request, "pathly/routes.html", {
      "places": sorted_groups,
      "api_key": api_key
    })

@login_required
def adminkml(request):
    places = get_places(request)

    return render(request, "pathly/adminkml.html", {
      "places": places
    })

@login_required
def sorting(request):
    places = get_places(request)

    if not places:
      return redirect("index")
    
    sorted_places = sort_locations(places)
    
    return render(request, "pathly/sorting.html", {
      "places": sorted_places
    })

@login_required
def manual_sorting(request):
    places = get_places(request)

    if not places:
      return redirect("index")
    
    sorted_places = sort_locations(places)
    
    return render(request, "pathly/manual_sorting.html", {
      "places": sorted_places
    })

@login_required
def about(request):
    return render(request, "pathly/about.html")

@login_required
def logout_view(request):
  if request.method == "POST":
    logout(request)
    return redirect("login_view")
  
  return redirect("index")
  
#helper functions
@login_required
def save_groups(request):
  if request.method == "POST":
    groups = request.session.get("sorted_groups")
    places = request.session.get("places")

    groupsaves = Groupsaves.objects.create(
      user=request.user,
      groups=groups,
      places=places
    )

    groupsaves.save()

  return JsonResponse({"Success": True})

@login_required
def handle_kml(request):
  if request.method == "POST":
    kml_file = request.FILES.get("kml_file")

    if not kml_file:
      return JsonResponse({"success": False})

    if kml_file:
      kml_file.seek(0)
      tree = ET.parse(kml_file)
      root = tree.getroot()

    places = {}
    styles = {}
    style_maps = {}

    ns = {
      "kml": "http://www.opengis.net/kml/2.2"
    }

    # Check markers in the root of the KML file and store them correctly in the dict
    for style in root.findall(".//kml:Style", ns):
      style_id = style.get("id")
      icon_href = style.find(".//kml:Icon/kml:href", ns)
      icon_color = style.find(".//kml:IconStyle/kml:color", ns)
      if style_id and icon_href is not None:
        kml_color = (
          icon_color.text.strip()
          if icon_color is not None
          else "ff000000"
        )

        css_color = (
          f"{kml_color[6:8]}"
          f"{kml_color[4:6]}"
          f"{kml_color[2:4]}"
        )

        styles[f"#{style_id}"] = {
          "icon": icon_href.text,
          "color": css_color
        }

    # Check StyleMap and store them in the dict
    for style_map in root.findall(".//kml:StyleMap", ns):
      style_map_id = style_map.get("id")

      for pair in style_map.findall("kml:Pair", ns):
        key = pair.find("kml:key", ns)
        style_url = pair.find("kml:styleUrl", ns)

        if (
          style_map_id
          and key is not None
          and key.text == "normal"
          and style_url is not None
        ):
          style_maps[f"#{style_map_id}"] = style_url.text

    placemarks = root.findall(".//kml:Placemark", ns)

    # Check placemarks in the KML file and store their data in a dict
    location_id = 0
    for placemark in placemarks[0:25]:
      name = placemark.find("kml:name", ns)
      coordinates = placemark.find(".//kml:coordinates", ns)
      styleUrl = placemark.find(".//kml:styleUrl", ns)
      style_url_text = styleUrl.text if styleUrl is not None else None

      resolved_style = style_maps.get(
        style_url_text,
        style_url_text
      )

      style_data = styles.get(resolved_style, {})
      icon_url = style_data.get("icon")
      icon_color = style_data.get("color", "#000000")
      coordinates_text = coordinates.text.strip()
      lon, lat, *_ = coordinates_text.split(",")
      places[name.text] = [
        f"{lat},{lon}",
        style_url_text,
        icon_url,
        icon_color,
        location_id
      ]

      location_id += 1
            
    # Find relevant extra info for each place
    places_extra_info = find_location_info(places)
    
    request.session["places"] = places
    request.session["kml_uploaded"] = True  
    request.session["places_extra_info"] = places_extra_info

    if kml_file:
      return JsonResponse({
        "success": True,
        "filename": kml_file.name,
        "size": kml_file.size,
      })

@login_required
def handle_specifications(request):
  if request.method == "POST":
    data = json.loads(request.body)

    specifications = data.get("specifications", [])
    group_amount = int(data.get("groupAmount"))

    # Apply specifications to the places and create the groups
    groups = apply_specifications(request, get_places(request), specifications, group_amount)

    return JsonResponse({
      "success": True,
      "groups": groups
      })
  
  else:
    return JsonResponse({"success": False, "error": "Invalid request method."})
  
def apply_specifications(request, places, specifications, group_amount):
  locations = []

  for name, place_data in places.items():
    locations.append({
      "id": place_data[4],
      "name": name,
      "coordinates": place_data[0],
      "marker": place_data[1]
    })

  # Shuffle locations to not get the same groups every time
  random.shuffle(locations)

  # Create groups based on specifications
  valid_groups = create_groups(locations, specifications, group_amount)

  # If there are still invalid locations, retry to add them in groups (TODO)

  # Store the sorted groups in the session for easier access
  sorted_groups = {}

  for index, group in enumerate(valid_groups, start=1):
    sorted_groups[f"group{index}"] = [
      location["id"]
      for location in group
    ]

  request.session["sorted_groups"] = sorted_groups

  return valid_groups

def create_groups(locations, specifications, group_amount):
  groups = []

  for location in locations:
    placed = False

    # Try to add location to a group, if not possible, create a new group
    for group in groups:
      if can_add_location(
        group,
        location,
        specifications,
        group_amount
      ):
        group.append(location)
        placed = True
        break

    if not placed:
      groups.append([location])

  valid_groups = []
  invalid_locations = []

  # Check groups for validity based on combine value, if not valid, add to invalid list
  for group in groups:
    if check_group_validity(group, specifications):
      valid_groups.append(group)
    else:
      invalid_locations.extend(group)
  
  # If there are still invalid locations, retry to add them in groups (TODO)
  return valid_groups

def can_add_location(group, location, specifications, group_amount):  
  if len(group) >= group_amount:
    return False

  marker_limit = None

  # Check if marker has a limit
  for spec in specifications:
    if spec["marker"] == location["marker"]:
      marker_amount = spec.get("markerAmount")

      if marker_amount:
        marker_limit = int(marker_amount)

      break

  # Check if adding location exceeds marker limit
  if marker_limit is not None:
    current_marker_amount = count_markers(group, location["marker"])

    if current_marker_amount >= marker_limit:
      return False
    
  # Prevent forbidden marker combinations in both directions
  for spec in specifications:
    if spec["marker"] == location["marker"]:
      forbidden_marker = spec.get("notCombine")

      if forbidden_marker and count_markers(group, forbidden_marker) > 0:
        return False
      
    if spec.get("notCombine") == location["marker"]:
      if count_markers(group, spec["marker"]) > 0:
        return False
      
  if exceeds_cap(group, location, specifications):
    return False
  
  return True

def check_group_validity(group, specifications):
  # Check if combination of markers in the group is the amount it should be
  for spec in specifications: 
    marker = spec.get("marker")
    combine_marker = spec.get("combine")
    combine_amount = spec.get("combineAmount")

    if not marker or not combine_marker or not combine_amount:
      continue

    combine_amount = int(combine_amount)

    marker_amount_in_group = count_markers(group, marker)

    if marker_amount_in_group == 0:
      continue

    combined_amount_in_group = count_markers(
      group,
      combine_marker
    )

    if combined_amount_in_group < combine_amount:
      return False
    
  return True

def exceeds_cap(group, location, specifications):
  group_with_location = group + [location]

  for spec in specifications:
    cap_enabled = spec.get("cap")

    if not cap_enabled:
      continue

    marker = spec.get("marker")
    combine_marker = spec.get("combine")
    cap_amount = spec.get("capAmount")

    if not marker or not combine_marker or not cap_amount:
      continue

    if count_markers(group_with_location, marker) == 0:
      continue

    cap_amount = int(cap_amount)

    if count_markers(group_with_location, combine_marker) > cap_amount:
      return True
    
  return False
  

def count_markers(group, marker):
  return sum(
    1
    for location in group
    if location["marker"] == marker
  )

def sort_locations(places):
  sorted_places = {}

  for place, place_data in places.items():
    marker_code = place_data[3]

    # add new marker code to the dict if that marker code isn't already present
    if marker_code not in sorted_places:
      sorted_places[marker_code] = {
        "icon": place_data[2],
        "color": f"#{place_data[3]}",
        "locations": [],
      }
    sorted_places[marker_code]["locations"].append({
      "name": place,
      "id": place_data[4]
    })

  return sorted_places

@login_required
def sort_manually(request):
  if request.method == "POST":
    data = json.loads(request.body)

    groups = data.get("groups", [])

    manual_groups = {}

    for group in groups:
      group_id = group["groupId"]
      locations = group["locationIds"]

      manual_groups[group_id] = locations

    print(manual_groups)

    request.session["sorted_groups"] = manual_groups
      
    return JsonResponse("success", safe=False)
  
  else:
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def calculate_route(request):
  data = json.loads(request.body)
  chosen_group = data["chosenGroup"]

  origin = data["origin"]
  destination = data["destination"]

  url = "https://routes.googleapis.com/directions/v2:computeRoutes"

  headers = {
     "Content-Type": "application/json",
     "X-Goog-Api-Key": get_credentials(),
     "X-Goog-FieldMask": (
       "routes.duration,"
       "routes.distanceMeters,"
       "routes.optimizedIntermediateWaypointIndex,"
       "routes.polyline.encodedPolyline"
     )
   }

  associated_locations_ids = request.session["sorted_groups"][chosen_group]
  
  locations_by_id = get_locations_by_id(get_places(request))

  associated_locations = []

  for location_id in associated_locations_ids:
    location = locations_by_id.get(int(location_id))

    if location:
      associated_locations.append(location)

  relevant_associated_locations = []

  for i in range(len(associated_locations)):
    coords = associated_locations[i]["coordinates"]
    lat, lng = coords.split(",")

    location_data = {
      "location": {
        "latLng": {
          "latitude": lat,
          "longitude": lng
        }
      }
    }

    relevant_associated_locations.append(location_data)

  google_route_data = {
    "origin": {
      "location": {
        "latLng": {
          "latitude": origin["coordinates"]["lat"],
          "longitude": origin["coordinates"]["lng"]
        }
      }
    },
    "destination": {
      "location": {
        "latLng": {
          "latitude": destination["coordinates"]["lat"],
          "longitude": destination["coordinates"]["lng"]
        }
      }
    },
    "intermediates": [],

    "travelMode": "DRIVE",
    "optimizeWaypointOrder": True
  }

  google_route_data["intermediates"] = (relevant_associated_locations)

  response = requests.post(
    url,
    headers = headers,
    json=google_route_data
  )

  result = response.json()

  optimized_indexes = result["routes"][0]["optimizedIntermediateWaypointIndex"]

  optimized_locations = [
    associated_locations[i]
    for i in optimized_indexes
  ]

  for location in optimized_locations:
    lat, lng = location["coordinates"].split(",")

    location["coordinates"] = {
      "lat": float(lat),
      "lng": float(lng)
    }


  route_result = {
    "origin": origin,
    "destination": destination,
    "intermediates": optimized_locations,
    "polyline": result["routes"][0]["polyline"]["encodedPolyline"],
    "distance": result["routes"][0]["distanceMeters"],
    "duration": result["routes"][0]["duration"],
  }

  return JsonResponse(route_result)

# Internal functions
def get_places(request):
  return request.session.get("places")

def get_credentials():
  load_dotenv()
  api_key = os.getenv("API_KEY")
  return api_key

def find_location_info(places):
  places_extra_info = {}
  api_key = get_credentials()

  # Check each place and add relevant information to the dictionary
  for place in places:
    coordinates = places[place][0]
    url = (
      f"https://maps.googleapis.com/maps/api/geocode/json"
      f"?latlng={coordinates}"
      f"&key={api_key}"
    )
    response = requests.get(url).json()
    components = response["results"][0]["address_components"]
  
    city = None
    province = None
    postcode = None

    for component in components:
      if "locality" in component["types"]:
        city = component["long_name"]

      elif "administrative_area_level_1" in component["types"]:
        province = component["long_name"]

      elif "postal_code" in component["types"]:
        postcode = component["long_name"]

    places_extra_info[place] = city, province, postcode
  
  return places_extra_info

def get_locations_by_id(places):
  locations_by_id = {}

  for name, place_data in places.items():
    location_id = place_data[4]
    locations_by_id[location_id] = {
      "name": name,
      "coordinates": place_data[0],
      "marker": place_data[1],
      "marker_icon": place_data[2],
      "marker_color": place_data[3]
    }

  return locations_by_id