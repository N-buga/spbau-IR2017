/**
 * Created by nadya-bu on 08/12/2017.
 */

function initMap(access_token) {
    var e = document.getElementById("city");
    var coords = e.options[e.selectedIndex].value;
    var lt = 59.942888;
    var lg = 30.303804;
    var place_name = "Санкт-Петербург";
    if(coords === "") {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                    function(position) {
                        lt = position.coords.latitude;
                        lg = position.coords.longitude;
                        place_name = "Ваш город";
                    }, function() {}
            );
        }
    } else {
        var pieces = coords.split(",");
        lt = pieces[0];
        lg = pieces[1];
        console.log("lt", lt);
        console.log("lg", lg);
        place_name = e.options[e.selectedIndex].text;
    }

    var mymap = L.map('mapid').setView([lt, lg], 13);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: access_token
    }).addTo(mymap);
    var marker = L.marker([lt, lg]).addTo(mymap);
    marker.bindPopup(place_name);
}

function sendQuery() {
    var input = document.getElementById("mySearch");
    var query = input.value;
    var select_list = document.getElementById("city");
    var city = select_list.options[select_list.selectedIndex].text;
    console.log(query);
    var place = document.getElementById("serp-list");

    var connection = new WebSocket('https://8b7a8020.ngrok.io');
    connection.onopen = function () {
        place.textContent = "Selecting the best events...";
        connection.send(city + "\n" + query);
    };

    connection.onmessage = function (msg) {
        // if (inProcessInterval != undefined) {
        //     clearInterval(inProcessInterval);
        // }
        var results = msg.data.split("\n\n");
        console.log("results", results);
        var error_code = results[0];
        var access_token = results[1];
        var new_url;
        var new_result;
        var new_context;
        if (error_code == "0") {
            alert('Internal error. Please, try again.');
        } else {
            place.textContent = "";
            var elem = document.getElementById("messages");
            if (error_code == "1") {
                elem.textContent = "";
                for (var i = 2; i < results.length; ++i) {
                    console.log("i: ", i, " results.length: ", results.length);

                    new_result = results[i].split("\t"); // it should give a two-element array
                    if(new_result.length == 0) {
                        continue;
                    }

                    new_url = new_result[0];
                    console.log("new_url: ", new_url);

                    var url = document.createElement("a");
                    url.setAttribute("href", new_url);
                    url.textContent = new_url;

                    var newElement = document.createElement("li");
                    newElement.setAttribute("class", "snippet");
                    newElement.appendChild(url);

                    if(new_result.length == 1) {
                        place.appendChild(newElement);
                        continue;
                    }

                    new_context = new_result[1].split("\n");
                    console.log("new_context: ", new_context);

                    var context = document.createElement("div");
                    for(var j = 0; j < new_context.length; j++) {
                        var pieces0 = new_context[j].split("<span style=\"color: #00a93b;font-weight:bold\">");

                        console.log("pieces0", pieces0);

                        if(pieces0.length < 2) {
                            continue;
                        }
                        var pieces1 = pieces0[1].split("</span>");

                        var p1 = pieces0[0];
                        var p2 = pieces1[0];
                        var p3 = pieces1[1];

                        var el1 = document.createElement("span");
                        var el2 = document.createElement("span");
                        el2.setAttribute("style", "color: #00a93b;font-weight:bold");
                        var el3 = document.createElement("span");
                        el1.textContent = p1;
                        el2.textContent = p2 + " ";
                        el3.textContent = p3 + "\n";

                        context.appendChild(el1);
                        context.appendChild(el2);
                        context.appendChild(el3);
                        context.appendChild(document.createElement("br"));
                    }
                    newElement.appendChild(context);
                    place.appendChild(newElement);
                }
                initMap(access_token);
            } else {
                elem.textContent = results[2];
            }
        }
    };
}

