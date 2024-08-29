var key = ''
$.ajax({
    type: "GET",
    dataType: 'json',
    url: '/get_api_key',
    data: {},
    async: false,
    success: function(success) {
        if (success){
            key = success.key;
        }
    },
});


var line = '<script async src="https://maps.googleapis.com/maps/api/js?key='+key+'&callback=initMap"></script>'
document.write(line);

function initialize_gmap(lat_long) {
    initMap(lat_long);
}

function initMap(lat_long) {
    /**
     * @license
     * Copyright 2019 Google LLC. All Rights Reserved.
     * SPDX-License-Identifier: Apache-2.0
     */
    let map;
    const chicago = { lat: 41.85, lng: -87.65 };

    /**
     * Creates a control that recenters the map on Chicago.
     */
    function createCenterControl(map) {
      const controlButton = document.createElement("button");

      // Set CSS for the control.
      controlButton.classList.add('buttonStyle');

      controlButton.textContent = "Center Map";
      controlButton.title = "Click to recenter the map";
      controlButton.type = "button";
      // Setup the click event listeners: simply set the map to Chicago.
      controlButton.addEventListener("click", () => {
        map.setCenter(chicago);
      });
      return controlButton;
    }

    function initMap(lat_long) {
    let myLatLng = {}
    if (lat_long && lat_long[0]) {
        myLatLng = { lat: parseFloat(lat_long[0][1]), lng: parseFloat(lat_long[0][2]) };
    }

      map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: myLatLng,
      });

        var marker = new google.maps.Marker({
        position: myLatLng,
        map,
        title: "",
        });
        let map_content = ''
        if (lat_long && lat_long[0]){
            map_content = lat_long[0][0]
        }
        else{
            map_content = ''
        }
        var infowindow = new google.maps.InfoWindow({
            content: map_content
        });

        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(map,marker);
        });


      // Create the DIV to hold the control.
      const centerControlDiv = document.createElement("div");
      // Create the control.
      const centerControl = createCenterControl(map);

      // Append the control to the DIV.
      centerControlDiv.appendChild(centerControl);
      map.controls[google.maps.ControlPosition.TOP_CENTER].push(
        centerControlDiv
      );
    }

    window.initMap = initMap;
}

