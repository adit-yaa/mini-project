var API1="http://localhost:8080/channel";
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
    console.log('Request failed', error);
  })

result.then(function(r) {
  var videoArr=r.items;
  var i=0;
  for (video of videoArr){
    make_video_carousel(video.snippet.resourceId.videoId, video.snippet.thumbnails.high.url ,video.snippet.title, i);
    make_video_list(video.snippet.resourceId.videoId, video.snippet.thumbnails.high.url ,video.snippet.title, i, video.snippet.description)
    i+=1;
  }
});

// function make_video_list(id, thumbnail, video_title){
//   var ul = document.getElementById("video-list");
//   var li = document.createElement("li");
//   var hr = document.createElement("hr");
//   var a = document.createElement("a");
//   var img = document.createElement("img");
//   img.setAttribute("src", thumbnail);
//   a.appendChild(img);
//   a.appendChild(document.createTextNode(" "+video_title+" "));
//   a.setAttribute("href","/"+id);
//   li.appendChild(a);
//   li.setAttribute("id", id);
//   ul.appendChild(li);
//   ul.appendChild(hr);
// }
function make_video_carousel(id, thumbnail, video_title, i){
  var ul = document.getElementById("video-list");
  var li = document.createElement("li");
  var div = document.getElementById("video-list-container");
  
  var carousel_item = document.createElement("div");
  var img = document.createElement("img");
  var caption = document.createElement("div");
  var caption_heading = document.createElement("h3")
  caption_heading.appendChild(document.createTextNode(video_title));
  caption.appendChild(caption_heading);
  img.setAttribute("src", thumbnail);
  caption.setAttribute("class", "carousel-caption");
  carousel_item.appendChild(img);
  carousel_item.appendChild(caption);
  
  if(i==0){
    carousel_item.setAttribute("class", "carousel-item active");
  }else{
    carousel_item.setAttribute("class", "carousel-item");
  }
  div.appendChild(carousel_item);

  li.setAttribute("data-target", "#demo");
  li.setAttribute("data-slide-to", i);
  li.setAttribute("id", id);
  ul.appendChild(li);
}
function make_video_list(id, thumbnail, video_title, i, video_desc){
  video_cards = document.getElementById("video-cards");
  col = document.createElement("div");
  a = document.createElement("a");
  card = document.createElement("div");
  img = document.createElement("img");
  card_body = document.createElement("div");
  video_heading = document.createElement("h4");
  p = document.createElement("p");

  video_heading.appendChild(document.createTextNode(video_title));
  video_heading.setAttribute("class","card-title");
  card_body.appendChild(video_heading);
  
  p.appendChild(document.createTextNode(video_desc));
  p.setAttribute("class", "card-text");
  card_body.appendChild(p);

  img.setAttribute("class", "card-img-top");
  img.setAttribute("src", thumbnail);
  img.setAttribute("alt", video_title);
  card.appendChild(img);

  card_body.setAttribute("class", "card-body");
  card.appendChild(card_body);
  
  card.setAttribute("class", "card");
  a.appendChild(card);

  a.setAttribute("href", "/"+id);
  a.setAttribute("role", "button");
  col.appendChild(a);
  
  col.setAttribute("class","col-md-4");
  if(i%3==0){
    row = document.createElement("div");
    row.appendChild(col);
    row.setAttribute("class","row");
    row.setAttribute("id","row"+i/3);
    video_cards.appendChild(row);
  }else{
    row = document.getElementById("row"+Math.floor( i/3 ));
    row.appendChild(col);
  }
}
