// function write_name(channel_name){
//   h2 = document.getElementById("name");
//   h2.appendChild(document.createTextNode(channel_name));
// }
// var API1="http://localhost:8080/channel";
// var result = fetch(API1, {
//     method: 'get',
//   }).then(function(response) {
//     return response.json();
//   }).then(function(data) {
//     var playlistId = data.items[0].contentDetails.relatedPlaylists.uploads;
//     return fetch(API1 + '/' + playlistId);
//   })
//   .then(function(response) {
//     return response.json();
//   })
//   .catch(function(error) {
//     console.log('Request failed', error)
//   })

// result.then(function(r) {
//   var videoArr=r.items
//   for (video of videoArr){
//     make_video_list(video.snippet.resourceId.videoId, video.snippet.thumbnails.default.url ,video.snippet.title)
//     write_name(video.snippet.channelTitle);
//   }
// });

// function make_video_list(id, thumbnail, video_title){
//   var corousel = document.getElementById("video-list");
//   var div = document.createElement("li");
//   var hr = document.createElement("hr");
//   var a = document.createElement("a");
//   var img = document.createElement("img");
//   img.setAttribute("src", thumbnail);
//   a.appendChild(img);
//   a.appendChild(document.createTextNode(" "+video_title+" "));
//   a.setAttribute("href","/"+id);
//   li.appendChild(a);
//   li.setAttribute("id", id);
//   carousel.appendChild(li);
// }

var currentLocation = window.location;
var API2=currentLocation.href+"/comments";
var result = fetch(API2, {
  method: 'get',
}).then(function(response) {
  return response.json();
}).then(function(data) {
  var comments = new Array();
  for (comment of data){
    let comment_json = {"id": comment.snippet.topLevelComment.id, "comment_text":comment.snippet.topLevelComment.snippet.textDisplay}
    comments.push(comment_json);
    make_comment_list(comment.snippet.topLevelComment.snippet.textDisplay);
  }
  document.getElementById("yt-iframe").src="https://www.youtube.com/embed"+currentLocation.pathname;
  return comments;
})
.catch(function(error) {
  console.log('Request failed', error);
})

result.then(function(r) {
    console.log(r);
    fetch('http://localhost:8080/OX0vlADFcIU/comments/analyse', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(r)
    }).then(response => {
      return response.json();
    }).then(function(data){
      console.log(data);
      barGraph(data.positive, data.toxic, data.severe_toxic, data.obscene, data.threat, data.insult, data.identity_threat);
      doughnutChart(data.positive, data.toxic, data.severe_toxic, data.obscene, data.threat, data.insult, data.identity_threat);
    })
    .catch(function(error) {
      console.log('Request failed', error);
    })
});

function make_comment_list(comment_text){
  container = document.getElementById("comment-container");
  document.getElementById("no-comment").innerHTML="";
  container.appendChild(document.createTextNode(comment_text));
  container.appendChild(document.createElement("hr"));
}

function canvas1data(positive, toxic, severe_toxic, obscene, threat, insult, identity_threat){
  return {
    labels: ['positive','toxic', 'severe_toxic','obscene','threat','insult','identity_hate'],
    datasets: [{
      label: '# of Votes',
      data: [positive, toxic, severe_toxic, obscene, threat, insult, identity_threat],
      backgroundColor: [
        'rgba(80, 220, 100, 1)',
        'rgba(240, 128, 128, 1)',
        'rgba(205, 92, 92, 1)',
        'rgba(220, 20, 60, 1)',
        'rgba(255, 0, 0, 1)',
        'rgba(178, 34, 34, 1)',
        'rgba(135, 0, 0, 1)'
      ],
      borderColor: [
        'rgba(80, 220, 100, 1)',
        'rgba(240, 128, 128, 1)',
        'rgba(205, 92, 92, 1)',
        'rgba(220, 20, 60, 1)',
        'rgba(255, 0, 0, 1)',
        'rgba(178, 34, 34, 1)',
        'rgba(135, 0, 0, 1)'
      ],
      borderWidth: 1
    }]
  }
}
function barGraph(positive, toxic, severe_toxic, obscene, threat, insult, identity_threat){
  var ctx = document.getElementById('canvas1').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'bar',
    data: canvas1data(positive, toxic, severe_toxic, obscene, threat, insult, identity_threat),
    options: {
      legend: {
        display: false
      },
      tooltips: {
        callbacks: {
          label: function(tooltipItem) {
            return tooltipItem.yLabel;
          }
        }
      }
    }
  });
}
function doughnutChart(positive, toxic, severe_toxic, obscene, threat, insult, identity_threat){
  var ctx = document.getElementById('canvas2').getContext('2d');
  var myChart = new Chart(ctx, {
      type: 'doughnut',
      data: canvas1data(positive, toxic, severe_toxic, obscene, threat, insult, identity_threat),
      options: {
        legend: {
          display: false
        }
      }
  });
}