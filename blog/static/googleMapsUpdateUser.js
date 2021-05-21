// Default location values to what is stored on the user record. If we're on the register page, set as null
var lat =(document.getElementById("id_lat") != null ? document.getElementById("id_lat").value : null);
var lng = (document.getElementById("id_long") != null ? document.getElementById("id_long").value : null);
var location_name = (document.getElementById("id_location_name") != null ? document.getElementById("id_location_name").value : null);
var travel_radius = (document.getElementById("id_travel_radius") != null ? document.getElementById("id_travel_radius").value : null);
var userId = (document.getElementById("user_id") != null ? document.getElementById("user_id").value : null);
const ROUND_NUM = 100000000; //round to 8th decimal place

let map;
var location_confirmed = false; //todo: prevent manipulation. Use let? Or validate on server side
var circleObject;


const source = document.getElementById('travel-radius');
function inputHandler(e) {
  travel_radius = e.target.value;
  circleObject.setRadius(travel_radius*1000); //update travel radius
  location_confirmed = false;
  circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //location no longer confirmed
  $('#confirm-location').empty();
}
source.addEventListener('input', inputHandler);


function updateUser() { // Called on click of update button
    if(travel_radius != null) {
        travel_radius = circleObject.getRadius()/1000; //Back end uses km, not m
    }

    $('#id_lat').val(Math.round(lat * ROUND_NUM) / ROUND_NUM);
    $('#id_long').val(Math.round(lng * ROUND_NUM) / ROUND_NUM);
    $('#id_travel_radius').val(travel_radius);
    $('#id_location_name').val(location_name);
}


function confirmLocation() {
    if(this.location_name != null) {
        $('#sign-up').empty();
        $('#confirm-location').empty();

        if(circleObject != null) {
            circleObject.setOptions({ fillColor: '#1ec71e', strokeColor: '#1ec71e' }); //set radius to green to indicate confirmed
        }
        $('#confirm-location').append('<p style="text-align: center; color: green; margin-top: 5px;">Location confirmed</p>');
        travel_radius = circleObject.getRadius();
        location_confirmed = true;
    }
    else {
        if(circleObject != null) {
            circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //set radius to red to indicate un-confirmed
        }
        $('#confirm-location').empty();
        $('#confirm-location').append('<p style="text-align: center; color: red; margin-top: 5px;">Please enter your City or Postal Code</p>')
    }
}


function initMap() {
    let initialCenter;

    initialCenter = { lat: parseFloat(lat), lng: parseFloat(lng) };
    $('#travel-radius').val(travel_radius); // initialize radius to what's stored on user
    $('#your-location-value').append('<span><b>' + this.location_name + '</b></span>');

    const map = new google.maps.Map(document.getElementById("map"), {
        center: initialCenter,
        zoom: 8,
        disableDefaultUI: true,
    });
    this.map = map;

    circleObject = new google.maps.Circle({ //draw initial circle w/ values from user
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map,
        center: initialCenter,
        radius: parseFloat(travel_radius)*1000, // Stored as km on user record. Convert to m
    });

    var options = {
        types: ['(regions)']
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
    marker.addListener("click", () => {
        infowindow.open(map, marker);
    });

    autocomplete.addListener("place_changed", () => { // If maps location is changed
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
            //$('#location-section').show(); // show "Your Location" and Travel Radius question
            $('#your-location-value').empty();
            $('#your-location-value').append('<span><b>' + this.location_name + '</b></span>');

            let lat = this.lat;
            let lng = this.lng;

            circleObject.setOptions({ fillColor: '#FF0000', strokeColor: '#FF0000' }); //location no longer confirmed
            circleObject.setRadius(circleObject.getRadius());
            circleObject.setCenter({lat, lng});
        }
        else { //if we received an invalid response from google (eg. empty location entered), show error
            $('#confirm-location').empty();
            $('#confirm-location').append('<p style="text-align: center; color: red; margin-top: 5px;">Please enter your City or Postal Code</p>')
            this.location_name = null;
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
