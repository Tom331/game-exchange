let map;
var circleObject;
var isAccountUpdatePage; //bool to track if we're on account page or register page
const ROUND_NUM = 100000000; //round to 8th decimal place

var lat;
var lng;
var location_name;
var travel_radius;
var location_confirmed = false; //todo: prevent manipulation. Use let? Or validate on server side


const source = document.getElementById('travel-radius');
function inputHandler(e) { //listen to update of travel_radius input
    travel_radius = e.target.value;
    circleObject.setRadius(travel_radius*1000); //update travel radius
    location_confirmed = false;
    circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //location no longer confirmed
    $('#confirm-location').empty();
}
source.addEventListener('input', inputHandler);


function validSignUp() { // Called on Update(acc update) or Submit (register)
    if(travel_radius != null) {
        travel_radius = circleObject.getRadius()/1000; //Back end uses km, not m
    }

    if(this.location_confirmed == true) {
        $('#sign-up').empty();
        $('#id_lat').val(Math.round(lat * ROUND_NUM) / ROUND_NUM);
        $('#id_long').val(Math.round(lng * ROUND_NUM) / ROUND_NUM);
        $('#id_travel_radius').val(travel_radius);
        $('#id_location_name').val(location_name);

        document.getElementById("register-form").submit();
    } else {
        $('#sign-up').empty();
        $('#sign-up').append('<p style="text-align: center; color: red; margin-top: 5px;">Please confirm your location</p>')
        return false;
    }
}


function confirmLocation() {
    if(location_name != null) {
        $('#sign-up').empty();
        $('#confirm-location').empty();

        if(circleObject != null) {
            circleObject.setOptions({ fillColor: '#1ec71e', strokeColor: '#1ec71e' }); //set radius to green to indicate confirmed
        }
        $('#confirm-location').append('<p style="text-align: center; color: green; margin-top: 5px;">Location confirmed</p>');
        travel_radius = circleObject.getRadius();
        this.location_confirmed = true;
    }
    else {
        if(circleObject != null) {
            circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //set radius to red to indicate un-confirmed
        }
        $('#confirm-location').empty();
        $('#confirm-location').append('<p style="text-align: center; color: red; margin-top: 5px;">Please enter your City or Postal Code</p>');
    }
}

function getSubmittedLocationValues() {
    if($('#id_lat').val() != null && $('#id_lat').val() != '') {
        lat = $('#id_lat').val();
    }
    if($('#id_long').val() != null && $('#id_long').val() != '') {
        lng = $('#id_long').val();
    }

    if($('#id_travel_radius').val() != null && $('#id_travel_radius').val() != '') {
        travel_radius = $('#id_travel_radius').val();
        $('#travel-radius').val(travel_radius); // initialize radius to what user entered on bad submission
    }

    if($('#id_location_name').val() != null && $('#id_location_name').val() != '') {
        $('#location-section').show();
        location_name = $('#id_location_name').val();
        $('#your-location-value').empty();
        $('#your-location-value').append('<span><b>' + location_name + '</b></span>');
    }

    let initialCenter;
    if(lat != null && lng != null) { // If the user submitted the form but forgot username/email/pass
        initialCenter = { lat: parseFloat(lat), lng: parseFloat(lng) };
    } else { // If first time loading the register page
        initialCenter = { lat: 49.245024, lng: -122.895993 }; // default to vancouver for register page
    }
    return initialCenter;
}


function initMap() {
    let initialCenter;
    $('#location-section').hide();

    // Get location values from the recent submission missing email, username or password
    initialCenter = this.getSubmittedLocationValues();

    const map = new google.maps.Map(document.getElementById("map"), {
        center: initialCenter,
        zoom: 8,
        disableDefaultUI: true,
    });
    this.map = map;

    if(lat != null && lng != null && travel_radius != null) { // If the user submitted the form but forgot username/email/pass
        travel_radius = travel_radius * 1000; //Just got travel_radius from form field, which has km value
        circleObject = new google.maps.Circle({
                strokeColor: "#FF0000",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#FF0000",
                fillOpacity: 0.35,
                map: map,
                center: initialCenter,
                radius: travel_radius,
            });
    }


    var options = {
        types: ['(regions)'] //allow countries, cities and postal codes to be searched
    };
    const input = document.getElementById("pac-input");
    const autocomplete = new google.maps.places.Autocomplete(input, options);
    autocomplete.bindTo("bounds", map);
    // Specify just the place data fields that you need.
    autocomplete.setFields(["place_id", "geometry", "name"]);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
    const infowindow = new google.maps.InfoWindow();
    const infowindowContent = document.getElementById("infowindow-content");
    infowindow.setContent(infowindowContent);
    const marker = new google.maps.Marker({ map: map });

    autocomplete.addListener("place_changed", () => { // listen for change of map location
        infowindow.close();
        const place = autocomplete.getPlace();

        //get lat and long from location
        let location = place.geometry.location;
        this.lat = location.lat();
        this.lng = location.lng();
        if(travel_radius == null || travel_radius == '') {
            travel_radius = 50000; //default to 50km
        }

        if(place.name != null && place.name != '') { //if we received a valid location from Google, update UI
            location_name = place.name;
            $('#confirm-location').empty();
            location_confirmed = false;
            $('#location-section').show(); // show "Your Location" and Travel Radius question
            $('#your-location-value').empty();
            $('#your-location-value').append('<span><b>' + location_name + '</b></span>');

            let lat = this.lat;
            let lng = this.lng;

            if(circleObject != null) { //user updated radius or the location
                circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //location no longer confirmed
                circleObject.setRadius(circleObject.getRadius());
                circleObject.setCenter({lat, lng});
            }
            else { //User selected a location for the 1st time, create a new circle
                circleObject = new google.maps.Circle({
                    strokeColor: "#FF0000",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#FF0000",
                    fillOpacity: 0.35,
                    map,
                    center: {lat, lng},
                    radius: travel_radius,
                });
            }
        }
        else { //if we received an invalid response from google (eg. empty location entered), show error
            $('#confirm-location').empty();
            $('#confirm-location').append('<p style="text-align: center; color: red; margin-top: 5px;">Please enter your City or Postal Code</p>')
            location_name = null;
            location_confirmed = false;
        }

        if (!place.geometry || !place.geometry.location) {
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
            map.setZoom(8);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(8);
        }
        // Set the position of the marker using the place ID and location.
        marker.setPlace({
            placeId: place.place_id,
            location: place.geometry.location,
        });
        marker.setVisible(true);
    });
}
