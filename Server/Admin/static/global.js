$(document).ready(function(){
	$('li').click(function() {
		if ($(this).hasClass('divider-vertical')){
			return;
		}
		$("li.active").removeClass("active");
		$(this).addClass('active');
		var toggle = $(this).find('a');
		var li_name = toggle.attr('id').substring(0, toggle.attr('id').indexOf('-'));
		$('#content-containers .container').hide();
		$('#' + li_name + '-container').show();
	});

	$("li.active").trigger('click');
});