
let new_event;
let map;
let info_windows = new Array();

$(document).ready(function() {

    if (window.location.pathname == "/") {
        popup();
    }

    $('#nav-toggle').click(function() {
        $('nav').toggleClass('expand-nav');
        $('#nav-list>li').toggleClass('show');
    });

    $('#create_event').click(function () {
        if (window.location.pathname != '/') {
            window.open("/", "_self", false);
        } else if (!new_event.getVisible()) {
            popup();
        } else {
            window.location = "/createevent?lat=" + new_event.getPosition().lat() +
                "&lng=" + new_event.getPosition().lng();
        }
    });

    function popup() {
        setTimeout(function() {
            let popup = $('#new_event_popup');
            popup.css('right', '0');
            setTimeout(function() {
                popup.css('right','-615px');
            }, 5000);
        }, 1000);
    }

});

// Create the map
function loadMap() {
    // The location of the John Harvard statue
    let john = {lat: 42.374434, lng: -71.117088};
    // The map, centered at John
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 16,
        center: john,
        disableDefaultUI: true,
        clickableIcons: false,
        styles:
            [{
                "featureType": "poi",
                "elementType": "labels.icon",
                "stylers": [{"visibility": "off"}]
            },
            {
                "featureType": "transit",
                "elementType": "labels",
                "stylers": [{"visibility": "off"}]
            }]
    });

    new_event = new google.maps.Marker({
        position: john,
        map: map,
        visible: false
    });

    google.maps.event.addListener(map, 'click', function(event) {
        new_event.setPosition(event.latLng);
        new_event.setVisible(true);
    });
};

function loadEvents(events) {
    for (let i = 0; i < events.length; i++) {
        createMarker(events[i]);
    }
}

function parseTime(start, end) {
    let timeStart = start.substring(11);
    let x = parseInt(timeStart.substring(0,2));
    timeStart = x > 12 ? String(x - 12) + timeStart.substring(2) + ' pm' : (x < 10 ? timeStart.substring(1) + ' am' : timeStart + ' am');

    let timeEnd = end.substring(11);
    x = parseInt(timeEnd.substring(0,2));
    timeEnd = x > 12 ? String(x - 12) + timeEnd.substring(2) + ' pm' : (x < 10 ? timeEnd.substring(1) + ' am' : timeEnd + ' am');
    return [start.substring(0, 11), timeStart + ' - ' + timeEnd];
}

function createMarker(info) {
    let m = new google.maps.Marker({
        position: JSON.parse(info["latlng"]),
        map: map
    });
    let time = parseTime(info.start, info.end);
    let windowContent = '<div class="IFcontent">' +
        '<p><span style="font-weight:700">' + info.title + '</span></p>' +
        '<p>' + info.location + '</p>' +
        '<p style="margin: 10px 0">' + info.description + '</p>' +
        '<p>' + time[0] + '</p>' +
        '<p>' + time[1] + '</p>' +
        '</div>';
    let i = new google.maps.InfoWindow({
        content: windowContent
    });

    info_windows.push(i);

    m.addListener('click', function() {
        let j;
        for (j = 0; j < info_windows.length; j++) {
            info_windows[j].close();
        }
        i.open(map, m);
    })
}