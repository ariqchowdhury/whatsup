window.whatsup = {}
whatsup.post_num = 0;

function get (el) {
	if (typeof el == 'string') return document.getElementById(el);
	return el;
}

$(document).ready(function(evt) {
	var ws;
	var host = "192.168.0.19";
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

		if (data.hasOwnProperty('num_users')) {
			UpdateUserCount(data);
		}
		else {
			AppendMessage(data);	
		}
		// Add message to message box
		
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

	var html_message =  "<div class='message_post' id='message_post_wrapper_" + whatsup.post_num + "'>" + 
						"<div class ='h6' id='message_post_user'>" +
						data.user + " : " + data.ts + " " + whatsup.post_num +
						"</div>" +
						"<div id='message_post_msg'>" +
						data.msg +
						"</div>" + 
						"</div>" +
						"</div>";

	get("messages").innerHTML += html_message;

	$(".message_post").click(function() {
		var element = event.target.id
		
		if (String(element).indexOf("wrapper") != -1) {
			// get(element).style.visibility="hidden";
			// console.log(get(element).parentNode);
			get(element).parentNode.removeChild(get(element));
		}

		// console.log(element);

		// get(element).parentNode.removeChild(element);
		
	})

	whatsup.post_num++;
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

function UpdateUserCount(data) {
	document.getElementById('time').innerHTML = "Number of Users: " + data.num_users;
}