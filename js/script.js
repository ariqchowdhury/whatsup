$(document).ready(function(evt) {
	var ws;
	var host = "localhost"
	var port = "8888"
	var uri = "/ws"

	ws = new WebSocket("ws://" + host + ":" + port + uri);

	ws.onopen = function(evt) {
		// send channel name and user name for client list
		// $("#ch_name").text();
	}

	ws.onmessage = function(evt) {
		received_message = JSON.parse(evt.data);
		$(".messages").append("<p>" + received_message.msg + "</p>");
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