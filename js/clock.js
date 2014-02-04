function startTime() {
	var today = new Date();

	var h = today.getUTCHours();
	var m = today.getUTCMinutes();
	var s = today.getUTCSeconds();

	m = ( m < 10 ? "0" : "") + m;
	s = ( s < 10 ? "0" : "") + s;
	document.getElementById('time').innerHTML = h + ":" + m + ":" + s + " UTC";
	t = setTimeout(function(){startTime()}, 500);
}
