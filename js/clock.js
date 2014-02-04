function startTime() {
	var today = new Date();

	var h = today.getUTCHours();
	var m = today.getUTCMinutes();
	var s = today.getUTCSeconds();

	m = checkTime(m);
	s = checkTime(s);
	document.getElementById('time').innerHTML = h + ":" + m + ":" + s + " UTC";
	t = setTimeout(function(){startTime()}, 500);
}

function checkTime(i) {
	if (i < 10) {
		i = "0" + i;
	}
	return i;
}