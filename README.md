# Pathly

Web application that will display an optimized route with intermediate waypoints based on user-chosen settings, route calculation via Google Maps Platform.

## 1: Distinctiveness and Complexity
For the final project, we needed to create a web application that is sufficiently difficult to create. I spent months thinking about what direction to take, and creating a Google Maps based route optimizer was an idea that came to mind after some discussions.

I wanted the project to have the following included:
- API integration, in this case Google Maps
- Multiple view routes
- User/registration based system
- User input 
- Something unique, a simple to-do list is in my opinion not reflective of the skills we've learned and what we want to be able to do
- A model aside from the User model that proves to be worth the time and effort
- Some sort of practical usage
- A project that I'd originally deem a bit too extensive and difficult, to challenge myself and greatly increase my skills

I knew from the start that my skills as a web developer were mainly focused on the backend side of development, so I wanted to incorporate modern techniques in the backend.
I know my frontend skills aren't nearly as developed, when starting the project, I thought about using React combined with Django to sharpen my frontend fundamentals as well, but I dropped this idea because then I'd get a product that, in my opinion, firstly does not reflect my current position as a developer, which is focused on making things work behind what the user sees, and secondly it would take way longer to learn a second framework and include that in the project.

After finishing the 'beta' of the webapp, which is what I call the version delivered in the submission, I feel like I've gone beyond what I expected of myself when I started this project. 
Quite honestly, finishing all the projects we have in the past CS50 and CS50W problem sets trained me as a developer way better than I expected. The foundation for becoming a good developer in the future is solid, and I am very happy that I managed to make this project work.

Further clarifying why I believe this project satisfies the distinctiveness and complexity requirements, some of the implementations in this project which we (I think) have not worked with in the problem sets before to this extent, include:
- Modern API integration (we have used some API here and there, the Bitcoin project in CS50, but not to this extent)
- Frontend and backend communication
- Geocoding
- Extensive checks in the routing to ensure no unwanted behaviour is executed
- Multiple helper and utility functions
- Dynamic usage of user input, in this case the sorting of the provided locations

## 2: Features
### 2.1 Authentication
- Registration
- Login / Logout
- User-specific data

### 2.2 Sorting
- User input via KML file upload
- Fully dynamic sorting algorithm
- Ability to add specifications to the algorithm (this was quite unorthodox, more on this later)
- Manual sorting ability
- Ability to save the sorted groups to either create a route, or save it to the database

### 2.3 Routes and Places API
- Google Maps Platform APIs
- Polyline in JavaScript to display the optimized route

## 3: Technical implementation
### 3.1 Authentication:
The webapp uses standard Django authentication. There is no need to look beyond what Django itself provides, this is safe, reusable, easy to learn and we have experience with this. 
Because of this, I felt like at least one other model is the bare minimum, which later became GroupSaves.
GroupSaves model saves the sorted groups to the logged in user, which is convenient when a user visits the application later, otherwise they would have to upload the kml and sort the locations first every time.

### 3.2 Sorting:
This was by far the most difficult problem to conquer, it starts with being able to let the user upload a file that you can easily dissect and that could be used for a sorting algorithm, this proved to be a KML file. The uploading of this file can take some time, as the files are really big, and extracting all required info from them for hundreds of times is a large task.
The first difficulties arose when starting to pick apart said KML file. KML files come shipped with a bunch of data I do not need for this project. 
The main parts needed for this project are the location postal code, coordinates, name, and style (which is the provided marker in this case). These are stored in a dictionary (places).

In order to save some loading time, getting the location info is split into multiple functions. 
Picking the KML file apart is done within handle_kml, the different markers are stored in styles based on their color.
The function then goes through all different locations in the file and stores their name, coordinates, style code, icon (marker) url, icon color and the location id, the style code later proved to not be optimal, as it bugged in sorting.html by placing same-colored marker locations in different columns.
Places_extra_info then calls find_location_info to find some relevant information mainly for mapinfo.html, I wanted these dictionaries splitted, having the postal code, province etc in the regular places dict makes it more messy and it is not required on every page.

Then, going to the sorting mechanism itself, JavaScript collects all specifications, which are then sent to Django via a fetch call.
- handle_specifications in views collects these said specifications and applies them to all places to create the groups.

- Apply_specifications is called, which itself calls multiple other functions, the locations are stored in a locations list, I did this because the places dict itself is filled with too much noise.
The locations are then shuffled to prevent sorting them would result in the same groups every time.

- Apply_specifications calls create_groups, which takes in the locations, specifications and group_amount.
Create_groups loops through all locations and adds them to a group if the specifications allow for it, which is checked by can_add_location, if the requirements are not satisfied, i.e., the location cannot be added to the group, it creates a new group.
Can_add_location loops through all specifications to check if they are satisfied. Except for the minimum amount of combined locations in the group, as that is a requirement that can only be checked for at the end.
The specifications in this case are:
* The amount of locations with a certain marker must appear at most x many times in a group.
* A location with marker X can not be combined with y marker.
* A location with marker X should be combined with at least locations with marker Y, a hard cap amount can be added.

- After the groups are made, it loops through all groups to check_group_validity.
Check_group_validity counts the number of locations of different markings and if the minimum amount of locations requirement is met. 

- The function finally returns the valid_groups, sometimes locations in a group do not satisfy the check_group_validity, because the minimum amount isn't met, these get added to a list called invalid_locations. Invalid_locations will later get a new attempt to sort them to hopefully get them in a valid group, but as this is a small issue, I'll leave it for now.

- Going back to apply_specifications, the valid_groups are stored in the session, so the backend does not need to calculate all this every time they are needed, the groups are given a number.

- Manual sorting was added so the user isn't held back by their locations only being able to be randomly ordered. Manual sorting checks what locations are selected and, when add to group is clicked, adds them to the selected group.

- The sorted groups can be saved in routes.html, so the user does not need to upload their file and sort their locations every time they visit the webapp. The groups are stored in the database and are connected to the logged in user.

### 3.3 Routes and Places API
In order to calculate a route with the given locations and be able to give said route back to the user, the Google Maps API is used.
Google makes the use of these APIs user friendly and straightforward. Thus I wanted to include certain features they make available.

Routes API is used for waypoint optimization, while geocoding API is used for finding info on the locations, these both fall under the Google Developer Program.

The user is required to select an origin and a destination. Once this is done, the selected group and all of its locations combined with the origin and destination are sent to Django, which performs the API call here.
The relevant locations are stored and looked up using the location ID. In order to be able to make the Google Maps API call, the data needs to be sent specifically, that is why the relevant_associated_locations are stored the way they are. optimizeWayPointOrder needs to be set to true so the locations will be ordered based on the fastest route.
The response is the optimized route. I store the intermediates again to have their data sorted in a way so that they can be sent to Google to create the polyline.
JavaScript then gets the result and puts the relevant data in googleMapsUrl, this too, is documented nicely in their developer program. This is done so that the user can visit the route on Google Maps, instead of only in the webapp.
displayRoute is called, this takes the polyline and shows it to the user, the polyline is basically an encoded string that Google Maps uses to know what route to display.

## 4: Issues 
During the development, I encountered and solved multiple .
Some of the issues include:
- The helper functions in views.py became really big, even still, some functions are about 100 lines of code. Also, sometimes the functions violated the single-responsibility-principle, so the functions needed to be split into multiple other functions. apply_specifications is the best example, it used to handle everything, but it became too large and I had to divide its responsibility, this took quite some time to implement in a way that made sense. The function is now divided into multiple helper functions that all keep a clear responsibility,
- The loading times for visiting a page were really long, this was because every time a page that required info on the places was visited, the KML file was read again, this was easy to fix by storing the data in the session once the file was uploaded. This is also why places and places_extra_info are separate.
- The KML file stores coordinates differently than how Google wants them in the API call, so that required some reorganisation.
- Crashes were frequent before I had the routes set up correctly, without uploading a KML file, the site would crash when visiting for example sorting.html, as get_places(request) could not return anything. So I wanted to force the user to register and log in first, and then send them to Admin KML firstly before anything else, that is why the routing is so strict.
- The sorting mechanism is really unorthodox, it took a long time understanding how the specification check could be acquired. Currently multiple functions are used to make sure all specifications are satisfied.
- I knew from previous problem sets that structuring your code in a correct manner is incredibly important to keep it readable and scalable, even though I knew this, I still had issues with it. For example places and places_extra_info were structured differently, which can result in really unnecessary bugs. I believe all dicts and lists that are used multiple times are now structured in a similar manner. This is something I want to do better in the future. 

## 5: Future improvements
- As explained earlier, my main skills in development are in the backend side. I understand relatively well how to read code and understand how data moves. This is why most time was deliberately spent toward application logic and functionality. Frontend on the other hand, is something I never really focused on and in which I can and should improve drastically. As you have likely noticed, the webapp has much to improve in the UI. The elements needed for a working application are there, and that is it, little time has been attributed to styling. This is something I want to focus next on, and this webapp is a good opportunity to get better at it.
- When a group doesn't satisfy the minimum combination requirement amount, the locations get added to the invalid_groups list, this is rarely an issue so I did not see the need to retry the sorting process with these immediately, it is however something for the future to look at.