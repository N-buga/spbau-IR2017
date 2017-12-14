/**
 * Created by nadya-bu on 08/12/2017.
 */

function sendQuery() {
    var input = document.getElementById("mySearch");
    var query = input.value;
    console.log(query);
    var place = document.getElementById("serp-list");

    var connection = new WebSocket('ws://localhost:9999');
    connection.onopen = function () {
//         alert('Getting result!');
         place.textContent = "In process...";
        //  inProcessInterval = setInterval(function() {
        //     answerParagraph.textContent = answerParagraph.textContent + ".";
        // }, 1000);
        connection.send(query);
    };

    connection.onmessage = function (msg) {
        // if (inProcessInterval != undefined) {
        //     clearInterval(inProcessInterval);
        // }
        var results = msg.data.split("\n");
        var error_code = results[0];
        var new_url;
        if (error_code == "0") {
            alert('Internal error. Please, try again.');
        } else {
            place.textContent = "";
            var elem = document.getElementById("messages");
            if (error_code == "1") {
                elem.textContent = "";
                for (var i = 1; i < results.length; ++i) {
                    new_url = results[i];
                    var url = document.createElement("a");
                    url.setAttribute("href", new_url);
                    url.textContent = new_url;
                    var newElement = document.createElement("li");
                    newElement.setAttribute("class", "snippet");
                    newElement.appendChild(url);
                    place.appendChild(newElement);
                }
            } else {
                elem.textContent = results[1];
            }
        }
    };
}

