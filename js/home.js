$(document).ready(function() {
	// Apply jquery_ui styled buttons 
	$("#signin").button();
	$("#register").button();
	$("#create_ch").button();

	// Use jquery_ui datepick widget
	$("#start_date").datepicker();
	$("#start_date").datepicker( "option", "showAnim", "slideDown");
	$("#start_date").datepicker( "option", "dateFormat", "yy-mm-dd");

	$("#signin").button().click(function () {
		$(this).closest("form").attr('action', '/login')
	});
	
	$("#register").button().click(function () {
		$(this).closest("form").attr('action', '/register')
	});

})