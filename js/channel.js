window.whatsup = {}
whatsup.id = $("#ch_id").text();

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
	
	ws = SetupWebsocket("ws://" + host + ":" + port + uri, id);

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

function SetupWebsocket(server, id) {
	var ws = new WebSocket(server);

	ws.onopen = function(evt) {
		SendInitMessage(ws, id);
	}

	ws.onmessage = function(evt) {
		data = JSON.parse(evt.data);

		if (data.hasOwnProperty('num_users')) {
			UpdateUserCount(data);
		}
		else {
			AppendMessageModule.constructor(data, ws);
			AppendMessageModule.append_to_dom();

		}
	};

	ws.onclose = function(evt) {
		
	}

	return ws;
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

function SendScoreMessage(websocket, id, user, comment_id, score_change) {
	var msg = {
		type: 'score',
		src: id,
		user: user,
		target: comment_id,
		score_change: score_change
	}

	websocket.send(JSON.stringify(msg));
}

var AppendMessageModule = (function () {
	var json_data;
	var is_short_msg;
	var html_message;
	var id_name_post_wrapper;
	var id_name_post_user;
	var ws;

	function constructor(data, websocket) {
		json_data = data;
		is_short_msg = (data.msg.length < 18);
		ws = websocket;
	}

	function create_html_of_message() {
		var html_message_root_class;
		post_num_uniq = json_data.comment_id;

		id_name_post_wrapper = "'" + post_num_uniq + "'"; 
		id_name_post_user = "'mpu_" + post_num_uniq + "'";

		if (is_short_msg) {
			html_message_root_class = "<div class='message_post short_message_post' id=" + id_name_post_wrapper;
		}
		else {
			html_message_root_class = "<div class='message_post long_message_post' id=" + id_name_post_wrapper;
		}

		html_message =  html_message_root_class + ">" + 
						"<div class ='h6 glow message_post_user' id=" + id_name_post_user + ">" +
						json_data.user + ":" + json_data.ts + " " + "<span class='message_score'>" + 0 + "</span>" + "</div>" +
						"<div class='glow message_post_msg' id='mpm_" + post_num_uniq + "'>" +
						json_data.msg + "</div>" + 
						"</div>";
	}

	function create_dom_element() {
		var new_div = document.createElement('div');
	
		if (is_short_msg) {
			destination_div = "short_messages_grid";
			new_div.style.marginLeft= (Math.floor(Math.random()* 18)).toString() + "%";
			html_message = "<li>" + html_message + "</li>";
		}
		else
			destination_div = "long_messages";

		new_div.innerHTML = html_message;
		var msg_div = get_element(destination_div);
		msg_div.appendChild(new_div);
		// Scroll to the top to newest message when the message box overflows
		msg_div.scrollTop = 0;
	}

	function add_handlers() {
		//id_name_* has quotes in it from making html, so strip those before using for jquery

		$("#" + id_name_post_wrapper.replace(/'/g, "")).click(function() {
			var element = event.target.id;
			
			// Check that the element name has 'wrapper' in it, so we know we clicked that and not
			// the text or user name divs of the element
			// This is needed because a click on a child element seems to go through to the parent as well
			if (String(element).indexOf("wrapper") != -1) {
				this.parentNode.removeChild(this);
			}		
		})

		$('#' + id_name_post_user.replace(/'/g, "")).on("click", function() {
			console.log(String(this.parentNode.id));
			SendScoreMessage(ws, whatsup.id, json_data.user, String(this.parentNode.id), 1);
		})		
	}

	function append_to_dom() {
		create_html_of_message();
		create_dom_element();
		add_handlers();
	}

	return {
		constructor: constructor,
		append_to_dom: append_to_dom
	}

})();

function UpdateUserCount(data) {
	document.getElementById('time').innerHTML = "Number of Users: " + data.num_users;
}