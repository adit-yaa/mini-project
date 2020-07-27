var API1="http://localhost:8080/channel";
var is_credential_present=0;
credential_present={{ credential_present }};

function write_name(channel_name){
    h2 = document.getElementById("name");
    h2.appendChild(document.createTextNode(channel_name));
}

var result = fetch(API1, {
        method: 'get',
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        var playlistId = data.items[0].contentDetails.relatedPlaylists.uploads;
        return fetch(API1 + '/' + playlistId);
    })
    .then(function(response) {
        return response.json();
    })
    .catch(function(error) {
        console.log('Request failed', error)
    })
  
result.then(function(r) {
    var videoArr=r.items
    write_name(videoArr[0].snippet.channelTitle);
});