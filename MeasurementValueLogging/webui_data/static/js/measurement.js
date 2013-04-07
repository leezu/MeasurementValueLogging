$(function() {
	setInterval(function() {
		$.getJSON($SCRIPT_ROOT + '/_get_values', {},
			function(data) {
				$(".display").remove()
				for (i = 0; i < data.len; i++) {
					$("<h2>")
					.text(data.displayvals[i] + " " + data.factors[i] + data.units[i])
					.addClass("display")
					.appendTo(".jumbo");
				}
			});
	}, 500);
});