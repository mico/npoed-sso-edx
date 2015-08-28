$(document).ready(function() {

    $(document).on("click", "#sub_reg_step1", function(e) {
        e.preventDefault();

        if($("#day").val() && $("#month").val() && $("#year").val()) {
            $("#id_date_of_birth").val([$("#month").val(), $("#day").val(), $("#year").val()].join("/"));
        };

        $.ajax({
            type: 'POST',
            url: "/home/",
            data: $("#reg_step1").serialize(),
            dataType: 'json',
            success: function(data) {
                if(data["status"] == "errors") {
                    $("#reg_step1 > .row-fluid").html(data["form"]);
                } else {
		    $('#click_accountsetup').trigger('click');
		}
	    },
        });	
    });

    $(document).on("click", "#form_sub", function(e) {
        e.preventDefault();

        if($("#day").val() && $("#month").val() && $("#year").val()) {
            $("#id_date_of_birth").val([$("#day").val(), $("#month").val(), $("#year").val()].join("/"));
        };

	$('#id_reg-username').val($("#id_reg-email").val());
	$('#id_reg-password2').val($("#id_reg-password1").val());
        $.ajax({
            type: 'POST',
            url: "/",
            data: $("#registr").serialize(),
            dataType: 'json',
            success: function(data) {
		console.dir(data);
                if(data["status"] == "ok") {
                    $("#registr").submit();
                } else {
                    $("#reg_body").html(data["reg_form"]);
                }
	    },
        });
    });
    
    $(document).on("click", "#auth_form_sub", function(e){
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: "/login_auth/",
            data: $("#login_auth").serialize(),
            dataType: 'json',
            success: function(data) {
                if(data["status"] == "ok") {
                    $("#login_auth").submit();
                } else {
                    $("#auth_form").html(data["form"]);
                }
	    },
        });
    });
});
