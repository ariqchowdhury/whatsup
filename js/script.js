$(document).ready(function(evt) {
	var ws;
	var host = "localhost";
	var port = "8888";
	var uri = "/ws";
	
	ws = new WebSocket("ws://" + host + ":" + port + uri);


	ws.onopen = function(evt) {
		// send channel name and user name for client list
		// $("#ch_name").text();
		SendInitMessage(ws);
	}

	ws.onmessage = function(evt) {
		data = JSON.parse(evt.data);
		// Add message to message box
		AppendMessage(data);
		// Scroll to newest message
		$("#messages").scrollTop($("#messages")[0].scrollHeight);
	};

	ws.onclose = function(evt) {
		SendCloseMessage(ws);
	}

	$("#send").click(function() {
		SendMessage(ws);
	})

	$("#send").button();

	$("#send_disabled").button();
	$("#send_disabled").button('option', 'disabled', true);

	$(document).keydown(function(event) {
		// If key pressed is 'enter'
		if (event.keyCode == 13 && !event.shiftKey) {
			SendMessage(ws);
		}
	})
})

function AppendMessage(data) {
	var html_message = "<div class='message_post'>" + 
						"<div id='message_post_user'>" +
						data.user + ":" +
						"</div>" +
						"<div id='message_post_ts'>" +
						data.ts +
						"</div>" +
						"<div id='message_post_msg'>" +
						data.msg +
						"</div>" + 
						"</div>";

	$("#messages").append(html_message);
}

// This function sends the text from the 'comment' textarea across the websocket
function SendMessage(websocket) {
	var comment = $("#comment").val();
	var id = $("#ch_id").text();
	var user = $("#user").text();

	var msg = {
		type: 'msg',
		src: id, 
		user: user,
		msg: comment
	}

	websocket.send(JSON.stringify(msg));
	$("#comment").val('');
}

function SendInitMessage(websocket) {
	var id = $("#ch_id").text();

	var msg = {
		type: 'init', 
		msg: id
	}

	websocket.send(JSON.stringify(msg));

}

function SendCloseMessage(websocket) {
	var id = $("#ch_id").text();

	var msg = {
		type: 'close', 
		msg: id
	}

	websocket.send(JSON.stringify(msg));
}