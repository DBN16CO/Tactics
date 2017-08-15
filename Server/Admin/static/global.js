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
		return "<button class='btn btn-warning user-edit' data-toggle='modal' data-target='#editUserModal'>Edit</button>" +
				"<div class='edit-user-data' data='" + JSON.stringify(data) + "' hidden='hidden'></div>" + 
				"<button class='btn btn-primary'>Reset Password</button>" + 
				"<button class='btn btn-primary'>Send Verification Email</button>" + 
				"<button class='btn btn-warning'>Ban</button>" + 
				"<button class='btn btn-danger'>Delete</button>";
	}

	$(".details-control-btn").on("click", function(){
		var tr = $(this).closest("tr");
		var row = userTable.row(tr);

		if (row.child.isShown()){
			$(this).html("+");
			row.child.hide();
			tr.removeClass("shown");
		}
		else{
			$(this).html("-");
			row.child(generateChildRow(row.data())).show();
			tr.addClass("shown");
		}
	});

	$("body").on("click", ".user-edit", function(){
		var data = $(this).siblings().attr("data");

		var user = JSON.parse(data);

		$(".edit-user-title").html("Edit User: " + user["Username"]);
		$("#edit-username").attr("value", user["Username"]);
		$("#edit-email").attr("value", user["Email"]);
		$("#edit-level").attr("value", user["Level"]);
		$("#edit-exp").attr("value", user["Experience"]);
		$("#user-id").attr("value", user["ID"]);
	});
});