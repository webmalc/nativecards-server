/** Global admin object **/

$(document).ready(function($) {
    'use strict';

    // Get images
    (function() {
        if ($('input#id_word').length) {
            $('div.field-remote_image').append(
                '<div id="remote-image-wrapper"></div>'
            );
        }
        $('input#id_word').blur(function(event) {
            $.get('/en/cards/images/?word=' + $(this).val(), function(data) {
                if (data['error']) {
                    console.log(data);
                    return;
                }
                let html = '';
                jQuery.each(data, function(index, item) {
                    html += '<img src="' + item['previewURL'] + '">';
                });
                $('#remote-image-wrapper').html(html);
                $('#remote-image-wrapper img').click(function() {
                    $('#remote-image-wrapper img').removeClass('chosen');
                    $(this).addClass('chosen');
                    $('input#id_remote_image').val($(this).attr('src'));
                    $('input#image-clear_id').prop('checked', true);
                });
            });
        });
    }());
});
