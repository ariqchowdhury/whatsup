window.whatsup = {}
whatsup.id = $("#ch_id").text();

whatsup.lambda_kappas = {};
whatsup.sigma_kappas = {};
whatsup.tau_lambda_kappas = {};
whatsup.tau_sigma_kappas = {};

var ttl;
whatsup.lambda_kappas_ttl = {};

var comment_type = {
	COMMENT: 0,
	REPLY: 1
};

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
		else if (data.hasOwnProperty('score')) {
			UpdateCommentScore(data);
		}
		else if (data.hasOwnProperty('reply_to')) {
			AppendMessageModule.constructor(data, ws, comment_type.REPLY);
			AppendMessageModule.append_to_dom();
		}
		else {
			AppendMessageModule.constructor(data, ws, comment_type.COMMENT);
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
		comment_id: comment_id,
		score_change: score_change
	}

	websocket.send(JSON.stringify(msg));
}

function ReplyToMessage(websocket, id, user, comment_id) {	
	var comment = $('#rc' + comment_id).val();

	var msg = {
		type: 'reply',
		src: id,
		user: user,
		comment_id: comment_id,
		msg: comment
	}

	websocket.send(JSON.stringify(msg));
}

var AppendMessageModule = (function () {
	var json_data;
	var is_short_msg;
	var html_message;
	var id_name_post_wrapper;
	var id_name_post_user;
	var id_name_post_msg;
	var id_reply_comment;
	var id_reply_area;
	var id_reply_btn;
	var mytype;
	var ws;

	function constructor(data, websocket, type) {
		json_data = data;
		is_short_msg = (data.msg.length < 18);
		ws = websocket;
		mytype = type;
	}

	function create_html_of_message() {
		var html_message_root_class;
		
		if (mytype == comment_type.COMMENT) {
			post_num_uniq = json_data.comment_id;
		} 
		else if (mytype == comment_type.REPLY) {
			post_num_uniq = json_data.reply_id;
		}
		else {
			console.log(mytype);	
		}

		id_name_post_wrapper = "'" + post_num_uniq + "'"; 
		id_name_post_user = "'mpu" + post_num_uniq + "'";
		id_name_post_msg = "'mpm" + post_num_uniq + "'";
		id_reply_comment = "'rc" + post_num_uniq + "'";
		id_reply_area = "'ra" + post_num_uniq + "'";
		id_reply_btn = "'b" + post_num_uniq + "'";

		var d = new Date(0);
		d.setUTCMilliseconds(json_data.ts);

		if (is_short_msg) {
			html_message_root_class = "<div class='message_post short_message_post' id=" + id_name_post_wrapper;
			whatsup.sigma_kappas[post_num_uniq] = 0;
			whatsup.tau_sigma_kappas[post_num_uniq] = json_data.ts;
			ttl = window.setTimeout(killme, 15000, post_num_uniq); 
		}
		else {
			html_message_root_class = "<div class='message_post long_message_post' id=" + id_name_post_wrapper;
			whatsup.lambda_kappas[post_num_uniq] = 0;
			whatsup.tau_lambda_kappas[post_num_uniq] = json_data.ts;
			whatsup.lambda_kappas_ttl[post_num_uniq] = window.setTimeout(killme, 20000, post_num_uniq);
		}

		var m = ( d.getUTCMinutes() < 10 ? "0" : "") + d.getUTCMinutes();

		html_message =  html_message_root_class + ">" + 
						"<div class ='h6 glow message_post_user' id=" + id_name_post_user + ">" +
						json_data.user + " " + d.getUTCHours()+":"+ m + " " + "<span class='message_score'>" + 0 + "</span>" + "</div>" +
						"<div class='glow message_post_msg' id=" + id_name_post_msg + ">" +
						json_data.msg + "</div>" + "<div class='reply_area' id=" + id_reply_area + 
						"><textarea class='reply_comment' id=" + id_reply_comment + " rows=3></textarea>" + 
						"</br> <button class='btn btn-primary btn-xs' type='submit' id=" + id_reply_btn + ">Reply</button></div>" +
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

		$("#" + id_name_post_wrapper.replace(/'/g, "")).on("click", function() {
			var element = event.target.id;

			// Check that the element name has 'wrapper' in it, so we know we clicked that and not
			// the text or user name divs of the element
			// This is needed because a click on a child element seems to go through to the parent as well
			if (String(element).indexOf("wrapper") != -1) {
				this.parentNode.removeChild(this);
			}		
		})

		$('#' + id_name_post_user.replace(/'/g, "")).on("click", function() {
			// CalculateScore();
			SendScoreMessage(ws, whatsup.id, json_data.user, String(this.parentNode.id), 1);
		})

		$('#' + id_name_post_msg.replace(/'/g, "")).on("click", function() {
			$('#ra' + String(this.parentNode.id)).slideToggle();		
		})

		$('#' + id_reply_btn.replace(/'/g, "")).on("click", function() {
			ReplyToMessage(ws, whatsup.id, json_data.user, String(this.parentNode.parentNode.id));
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

function UpdateCommentScore(data) {
	score = document.getElementById(data.comment_id).getElementsByClassName('message_score');
	// There will only be one element of class message_score, so it will be the first 
	var current_score = parseInt(score[0].innerText);
	current_score += 1;
	score[0].innerText = current_score;

	if (data.comment_id in whatsup.lambda_kappas) {
		whatsup.lambda_kappas[data.comment_id]++;
	}
	else if (data.comment_id in whatsup.sigma_kappas) {
		whatsup.sigma_kappas[data.comment_id]++;
	}

	if (data.comment_id in whatsup.lambda_kappas_ttl) {
		window.clearTimeout(whatsup.lambda_kappas_ttl[data.comment_id]);
		whatsup.lambda_kappas_ttl[data.comment_id] = window.setTimeout(killme, 8000, post_num_uniq);
	}

}

function killme(element) {
	var $comment_div = $("#" + element.replace(/'/g, ""));

	$comment_div.fadeOut(500, function() {		
		$comment_div.remove();	
	})
}