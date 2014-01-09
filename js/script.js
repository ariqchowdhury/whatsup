$(document).ready(function(evt) {
	var ws;
	var host = "localhost"
	var port = "8888"
	var uri = "/ws"

	ws = new WebSocket("ws://" + host + ":" + port + uri);

	ws.onmessage = function(evt) {
		$(".messages").append("<p>" + evt.data + "</p>");
	};

	$("#send").click(function() {
		SendMessage(ws);
	})

	$(document).keydown(function(event) {
		// If key pressed is 'enter'
		if (event.keyCode == 13 && !event.shiftKey) {
			SendMessage(ws);
		}
	})
})

// This function sends the text from the 'comment' textarea across the websocket
function SendMessage(websocket) {
	var comment = $("#comment").val();
	websocket.send(comment);
	$("#comment").val('');
}