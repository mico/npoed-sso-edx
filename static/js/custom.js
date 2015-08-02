/**
 * Created by sendr on 23.07.15.
 */


jQuery(document).ready(function ($) {
    //   script for choosing images

    $('.interest_choice a').on('click', function(){
      var check = $(this).next();
      if (check.prop('checked')) {
        check.removeAttr('checked');
        $(this).css('background-color', 'inherit');
      }
      else {
        check.prop('checked', 'checked');
        $(this).css('background-color', 'black');
      }
    });

    //    slideUp for course item

    $('.span-close').on('click', function(){
        $(this).parentsUntil('.close-modal').slideUp(300);
    });

    //                                 clideUp for del_element in book.html !!!!!!!temporarily!!!!!!!!!!!

    $('.del_element').on('click', function(){
        $(this).closest('.what_slideUp').slideUp(300);
    });

    //   for hover avatar show block

    $('.profile_photo').on('mouseenter', function () {
        $(this).children('div').css('display', 'block');
    });
    $('.profile_photo').on('mouseleave', function () {
        $(this).children('div').css('display', 'none');
    });

    //   for item_message

    $('.item_message_body').on('click', function(){
        document.location.href = '/message_exchange/';
    });
    $('.item_message_body').on('mouseenter', function(){
        $(this).css('cursor', 'pointer');

    });
    $('.item_message').on('mouseenter', function(){
        $(this).children('.panel-body').css('background', '#d3d3d3');

    });
    $('.item_message').on('mouseleave', function(){
        $(this).children('.panel-body').css('background', '#e7e7e7');
    })
    $('.grid').isotope({
      // options
      itemSelector: '.grid-item'
        //percentPosition: 'true',

    });
});
