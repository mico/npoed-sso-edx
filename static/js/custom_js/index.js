$(document).ready(function() {

    $("select").chosen();

    $(document).on("keypress", "input", function (e) {
    if (e.which == 13) {
        $(this).parents('form').submit();
        return false;
    }
    });

});
