import json
import os
import requests
import xml.etree.ElementTree as ET
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from dotenv import load_dotenv


# Create your views here.
def index(request):
  places = get_places(request)
  return render(request, "pathly/index.html", {
    "places": places
  })

def routes(request):
  places = get_places(request)

  return render(request, "pathly/routes.html", {
    "places": places
  })

def mapinfo(request):
  places = request.session.get("places_extra_info")

  return render(request, "pathly/mapinfo.html", {
    "places": places
  })

def about(request):
  places = get_places(request)
  return render(request, "pathly/about.html", {
    "places": places
  })

def sorting(request):
  places = get_places(request)
  sorted_places = sort_locations(places)

  return render(request, "pathly/sorting.html", {
    "places": sorted_places
  })

def adminkml(request):
  places = get_places(request)
  return render(request, "pathly/adminkml.html", {
    "places": places
  })


#helper functions
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
        icon_color
      ]
      
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
    
def get_places(request):
  return request.session.get("places")

def get_credentials():
  load_dotenv()
  api_key = os.getenv("API_KEY")
  return api_key
  
def find_location_info(places):
  places_extra_info = {}
  api_key = get_credentials()

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

def sort_locations(places):
  sorted_places = {}

  for place, place_data in places.items():
    marker_code = place_data[1]

    if marker_code not in sorted_places:
      sorted_places[marker_code] = {
        "icon": place_data[2],
        "color": f"#{place_data[3]}",
        "locations": []
      }
    sorted_places[marker_code]["locations"].append(place)

  return sorted_places

def handle_specifications(request):
  if request.method == "POST":
    data = json.loads(request.body)

    specifications = data.get("specifications", [])
    randomize = data.get("randomize", False)

    print(specifications)
    print(randomize)

    apply_specifications(get_places(request), specifications, randomize)

    return JsonResponse({"success": True})
  
  else:
    return JsonResponse({"success": False, "error": "Invalid request method."})
  
def apply_specifications(places, specifications, randomize):
  pass