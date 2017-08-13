$(document).ready(function(){
	$("li").click(function() {
		if ($(this).hasClass("divider-vertical")){
			return;
		}
		$("li.active").removeClass("active");
		$(this).addClass("active");
		var toggle = $(this).find("a");
		var liName = toggle.attr("id").substring(0, toggle.attr("id").indexOf("-"));
		$("#content-containers .container").hide();
		$("#" + liName + "-container").show();
	});

	$("li.active").trigger("click");
	$("#perf-table").DataTable();
	var userTable = $("#user-table").DataTable({
		"columns": [
			{"data": "ID"},
			{"data": "Username"},
			{"data": "Registered Date"},
			{"data": "Email"},
			{"data": "Verified"},
			{"data": "Last Login"},
			{"data": "Level"},
			{"data": "Experience"},
			{
				"className": "details-control",
				"orderable": false,
				"data": "Actions",
				"defaultContent": ""
			}
		]
	});

	function generateChildRow(data){
		return "<div class='row'>" + 
		          "<div class='col-xs-2'>" + 
		             "<button class='btn btn-warning'>Edit</button>" +
		          "</div>" + 
		          "<div class='col-xs-2'>" + 
		             "<button class='btn btn-primary'>Reset Password</button>" + 
		          "</div>" + 
		          "<div class='col-xs-2'>" + 
		             "<button class='btn btn-primary'>Send Verification Email</button>" + 
		          "</div>" + 
		          "<div class='col-xs-2'>" +
		             "<button class='btn btn-warning'>Ban</button>" + 
		          "</div>" + 
		          "<div class='col-xs-2'>" +
		             "<button class='btn btn-danger'>Delete</button>" + 
		          "</div>" + 
		          "<div class='col-xs-2'>" +
		          "</div>" + 
		        "</div>";
	}

	$(".details-control-btn").on('click', function(){
		var tr = $(this).closest('tr');
		var row = userTable.row(tr);

		if (row.child.isShown()){
			$(this).html("+");
			row.child.hide();
			tr.removeClass("shown");
		}
		else{
			$(this).html("-");
			row.child(generateChildRow(row.data())).show();
			tr.addClass('shown');
		}
	});
});