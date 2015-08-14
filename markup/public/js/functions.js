$( document ).ready(function() {

  $(".search-input").keypress(function(e) {
    if (e.which == 13) {
      e.preventDefault();
      $(e.currentTarget).parent().parent().submit();
    }
  });

  var ces = $(".competencies-educational-standard");
  ces.find(".switcher > a").click(function(e) {
    e.preventDefault();
    ces.toggleClass("js-show-more js-show-less");
  });

  if ($(".section-course").length) {
    $(".course-content-header").sticky({topSpacing:0});
  };

  $(".editable").click(function(event) {
    $(this).addClass('js-state-edit');
  });

});
