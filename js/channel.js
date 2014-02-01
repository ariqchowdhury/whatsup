$(document).ready(function(evt) {
	var ws;
	var host = "localhost";
	var port = "9000";
	var uri = "/ws";

	var id = $("#ch_id").text();
	var user = $("#user").text();
	
	ws = new WebSocket("ws://" + host + ":" + port + uri);


	ws.onopen = function(evt) {
		SendInitMessage(ws, id);
	}

	ws.onmessage = function(evt) {
		console.log(new Date().getTime());
		data = JSON.parse(evt.data);
		// Add message to message box
		AppendMessage(data);
		console.log(new Date().getTime());

		// Scroll to newest message
		$("#messages").scrollTop($("#messages")[0].scrollHeight);
	};

	ws.onclose = function(evt) {
		
	}

	$("#send").click(function() {
		SendMessage(ws, id, user);
	})

	$(document).keypress(function(event) {
		// If key pressed is 'enter'
		if (event.keyCode == 13 && !event.shiftKey) {
			event.preventDefault();
			SendMessage(ws, id, user);
		}
	})

})

function AppendMessage(data) {
	var html_message =  "<div class='message_post_wrapper'>" +
						"<div class='message_post'>" + 
						"<div id='message_post_user'>" +
						data.user +
						"</div>" +
						"<div id='message_post_ts'>" +
						data.ts +
						"</div>" +
						"<div id='message_post_msg'>" +
						data.msg +
						"</div>" + 
						"</div>" +
						"</div>";

	document.getElementById("messages").innerHTML += html_message;
	//$("#messages").append($(html_message).hide().fadeIn(200));//.fadeIn(150));
}

// This function sends the text from the 'comment' textarea across the websocket
function SendMessage(websocket, id, user) {
	var comment = $("#comment").val();

	var msg = {
		type: 'msg',
		src: id, 
		user: user,
		msg: comment
	}

	websocket.send(JSON.stringify(msg));
	$("#comment").val('');
}

function SendInitMessage(websocket, id) {

	var msg = {
		type: 'init', 
		msg: id
	}

	websocket.send(JSON.stringify(msg));

}
