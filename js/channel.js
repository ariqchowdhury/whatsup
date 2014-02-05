window.whatsup = {}
whatsup.post_num = 0;

function get_element (el) {
	if (typeof el == 'string') return document.getElementById(el);
	return el;
}

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

		if (data.hasOwnProperty('num_users')) {
			UpdateUserCount(data);
		}
		else {
			AppendMessage(data);	
		}
		
		console.log(new Date().getTime());

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
	var destination_div;
	var html_message =  "<div class='message_post' id='message_post_wrapper_" + whatsup.post_num + "'>" + 
						"<div class ='h6 glow' id='message_post_user'>" +
						data.user + " : " + data.ts + " " + whatsup.post_num +
						"</div>" +
						"<div class='glow' id='message_post_msg'>" +
						data.msg +
						"</div>" + 
						"</div>" +
						"</div>";

	if (data.msg.length < 18) {
		destination_div = "short_messages";
	}
	else
		destination_div = "long_messages";

	var new_div = document.createElement('div');
	new_div.innerHTML = html_message;
	new_div.style.marginLeft= (Math.floor(Math.random()* 45)).toString() + "%";

	var msg_div = get_element(destination_div);
	// Prepend new message to message box
	msg_div.appendChild(new_div);
	// Scroll to the top to newest message when the message box overflows
	msg_div.scrollTop = 0;

	$(".message_post").click(function() {
		var element = event.target.id
		
		if (String(element).indexOf("wrapper") != -1) {
			get_element(element).parentNode.removeChild(get_element(element));
		}		
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