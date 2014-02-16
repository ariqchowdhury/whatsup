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

Inheritance_Manager = {};
Inheritance_Manager.extend = function (subClass, baseClass) {
	function inheritance() { }
	inheritance.prototype = baseClass.prototype;
	subClass.prototype = new inheritance();
	subClass.prototype.constructor = subClass;
	subClass.baseConstructor = baseClass;
	subClass.superClass = baseClass.prototype;
}

Comment = function (websocket, json_data) {
	this.ws = websocket;
	this.data = json_data;	
}

Comment.prototype = {
	
	set_uniq_id: function() {
		this.post_num_uniq = this.data.comment_id;
	},

	generate_ids: function() {
		this.id_name_post_wrapper = "'" + this.post_num_uniq + "'"; 
		this.id_name_post_user = "'mpu" + this.post_num_uniq + "'";
		this.id_name_post_msg = "'mpm" + this.post_num_uniq + "'";
		this.id_reply_comment = "'rc" + this.post_num_uniq + "'";
		this.id_reply_area = "'ra" + this.post_num_uniq + "'";
		this.id_reply_btn = "'b" + this.post_num_uniq + "'";
	},

	generate_root_html: function() {
		this.html_message_root_class = "";
	},

	generate_html: function() {
		var d = new Date(0);
		d.setUTCMilliseconds(this.data.ts);

		var m = ( d.getUTCMinutes() < 10 ? "0" : "") + d.getUTCMinutes();

		this.html_message =  this.html_message_root_class + ">" + 
						"<div class ='h6 glow message_post_user' id=" + this.id_name_post_user + ">" +
						this.data.user + " " + d.getUTCHours()+":"+ m + " " + "<span class='message_score'>" + 0 + "</span>" + "</div>" +
						"<div class='glow message_post_msg' id=" + this.id_name_post_msg + ">" +
						this.data.msg + "</div>" + "<div class='reply_area' id=" + this.id_reply_area + 
						"><textarea class='reply_comment' id=" + this.id_reply_comment + " rows=3></textarea>" + 
						"</br> <button class='btn btn-primary btn-xs' type='submit' id=" + this.id_reply_btn + ">Reply</button></div>" +
						"</div>";
	},

	generate_dom_element: function() {
		this.new_div = document.createElement('div');
	},

	add_dom_element: function() {
		this.new_div.innerHTML = this.html_message;
		var msg_div = get_element(this.destination_div);
		msg_div.appendChild(this.new_div);
		// Scroll to the top to newest message when the message box overflows
		msg_div.scrollTop = 0;
	},

	add_handler: function() {
		ws = this.ws;
		data = this.data;
		$("#" + this.id_name_post_wrapper.replace(/'/g, "")).on("click", function() {
			var element = event.target.id;

			// Check that the element name has 'wrapper' in it, so we know we clicked that and not
			// the text or user name divs of the element
			// This is needed because a click on a child element seems to go through to the parent as well
			if (String(element).indexOf("wrapper") != -1) {
				this.parentNode.removeChild(this);
			}		
		})

		$('#' + this.id_name_post_user.replace(/'/g, "")).on("click", function() {
			// CalculateScore();
			SendScoreMessage(ws, whatsup.id, data.user, String(this.parentNode.id), 1);
		})

		$('#' + this.id_name_post_msg.replace(/'/g, "")).on("click", function() {
			$('#ra' + String(this.parentNode.id)).slideToggle();		
		})

		$('#' + this.id_reply_btn.replace(/'/g, "")).on("click", function() {
			ReplyToMessage(ws, whatsup.id, data.user, String(this.parentNode.parentNode.id));
		})
	}

}

ShortComment = function (websocket, json_data) {
	ShortComment.baseConstructor.call(this, websocket, json_data);
}

Inheritance_Manager.extend(ShortComment, Comment);

ShortComment.prototype.generate_root_html = function() {
	this.html_message_root_class = "<div class='message_post short_message_post' id=" + this.id_name_post_wrapper;
	whatsup.sigma_kappas[this.post_num_uniq] = 0;
	whatsup.tau_sigma_kappas[this.post_num_uniq] = this.data.ts;
	ttl = window.setTimeout(killme, 15000, this.post_num_uniq);
};

ShortComment.prototype.generate_dom_element = function() {
	this.new_div = document.createElement('div');
	this.destination_div = "short_messages_grid";
	this.new_div.style.marginLeft= (Math.floor(Math.random()* 18)).toString() + "%";
	this.html_message = "<li>" + this.html_message + "</li>";
};

LongComment = function (websocket, json_data) {
	LongComment.baseConstructor.call(this, websocket, json_data);
}
Inheritance_Manager.extend(LongComment, Comment);
LongComment.prototype.generate_root_html = function() {
	this.html_message_root_class = "<div class='message_post long_message_post' id=" + this.id_name_post_wrapper;
	whatsup.lambda_kappas[this.post_num_uniq] = 0;
	whatsup.tau_lambda_kappas[this.post_num_uniq] = this.data.ts;
	whatsup.lambda_kappas_ttl[this.post_num_uniq] = window.setTimeout(killme, 20000, this.post_num_uniq);
};

LongComment.prototype.generate_dom_element = function() {
	this.new_div = document.createElement('div');
	this.destination_div = "long_messages";
}

ReplyComment = function (websocket, json_data) {
	ReplyComment.baseConstructor.call(this, websocket, json_data);	
}
Inheritance_Manager.extend(ReplyComment, LongComment);
ReplyComment.prototype.set_uniq_id = function() {
	this.post_num_uniq = this.data.reply_id;
}

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
			cmnt = new ReplyComment(ws, data);
			add_to_dom(cmnt);
		}
		else {
			if (data.msg.length < 18) {
				cmnt = new ShortComment(ws, data);
			}
			else {
				cmnt = new LongComment(ws, data);
			}
			add_to_dom(cmnt);
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


function add_to_dom(comment) {
	comment.set_uniq_id();
	comment.generate_ids();
	comment.generate_root_html();
	comment.generate_html();
	comment.generate_dom_element();
	comment.add_dom_element();
	comment.add_handler();
}

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