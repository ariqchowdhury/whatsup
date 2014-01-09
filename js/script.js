$(document).ready(function(evt) {
	var ws;
	var host = "localhost"
	var port = "8888"
	var uri = "/ws"

	ws = new WebSocket("ws://" + host + ":" + port + uri);

	ws.onmessage = function(evt) {alert(evt.data)};

	$("#send").click(function() {
		var comment = $("#comment").val();
		ws.send(comment);
		$("#comment").val('');
	})
})