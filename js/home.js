$(document).ready(function() {
	// Apply jquery_ui styled buttons 
	$("#signin").button();
	$("#create_ch").button();

	// Use jquery_ui datepick widget
	$("#start_date").datepicker();
	$("#start_date").datepicker( "option", "showAnim", "slideDown");
	$("#start_date").datepicker( "option", "dateFormat", "yy-mm-dd");
})