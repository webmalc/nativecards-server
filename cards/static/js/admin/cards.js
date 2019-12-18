/** Global admin object **/

$(document).ready(function ($) {
    'use strict';

    // Add clear button
    (function () {
        $('<span id="clear-card">clear</span>').insertAfter($('#id_word'));
        $('#clear-card').click(function () {
            $(`textarea#id_definition, input#id_pronunciation, input#id_word,
               textarea#id_examples, input#id_translation,
               input#id_transcription, textarea#id_synonyms,
               textarea#id_antonyms`).val('').trigger('change');
        });
    }());

    // Get definition
    (function () {
        $('input#id_word').blur(function (event) {
            let definitionInput = $('textarea#id_definition');
            let pronunciationInput = $('input#id_pronunciation');
            let examplesInput = $('textarea#id_examples');
            let transcriptionInput = $('input#id_transcription');

            if (definitionInput.val() &&
                examplesInput.val() &&
                pronunciationInput.val() &&
                transcriptionInput.val()
            ) {
                return;
            }
            $.get(
                '/en/cards/definition/?word=' + $(this).val(),
                function (data) {
                    if (data.error) {
                        console.log(data);
                        return;
                    }
                    if (!pronunciationInput.val()) {
                        pronunciationInput.val(data.pronunciation);
                    }
                    if (!transcriptionInput.val()) {
                        transcriptionInput.val(data.transcription);
                    }
                    if (!examplesInput.val()) {
                        examplesInput.val(data.examples).
                            get(0).dispatchEvent(new Event('input'));
                    }
                    if (!definitionInput.val()) {
                        definitionInput.val(data.definition).
                            get(0).dispatchEvent(new Event('input'));
                    }
                });
        });
    }());

    // Get synonyms and antonyms
    (function () {
        $('input#id_word').blur(function (event) {
            let synonymsTextarea = $('textarea#id_synonyms');
            let antonymsTextarea = $('textarea#id_antonyms');
            if (synonymsTextarea.val() && antonymsTextarea.val()) {
                return;
            }
            $.get(
                '/en/cards/synonyms/?word=' + $(this).val(),
                function (data) {
                    if (data.error) {
                        console.log(data);
                        return;
                    }
                    if (!synonymsTextarea.val()) {
                        synonymsTextarea.val(data.synonyms).
                            get(0).dispatchEvent(new Event('input'));
                    }
                    if (!antonymsTextarea.val()) {
                        antonymsTextarea.val(data.antonyms).
                            get(0).dispatchEvent(new Event('input'));
                    }
                });
        });
    }());

    // Get translation
    (function () {
        $('input#id_word').blur(function (event) {
            let transInput = $('input#id_translation');
            if (!transInput.length || transInput.val()) {
                return;
            }
            $.get(
                '/en/cards/translation/?word=' + $(this).val(),
                function (data) {
                    if (data.error) {
                        return;
                    }
                    transInput.val(data.translation);
                });
        });
    }());

    // Get images
    (function () {
        if (!$('div.field-remote_image').length) {
            return;
        }
        if ($('input#id_word').length) {
            $('div.field-remote_image').append(
                '<div id="remote-image-wrapper"></div>'
            );
        }
        $('input#id_word').blur(function (event) {
            $.get('/en/cards/images/?word=' + $(this).val(), function (data) {
                if (data.error) {
                    console.log(data);
                    return;
                }
                let html = '';
                jQuery.each(data, function (index, item) {
                    html += '<img src="' + item.previewURL + '">';
                });
                $('#remote-image-wrapper').html(html);
                $('#remote-image-wrapper img').click(function () {
                    $('#remote-image-wrapper img').removeClass('chosen');
                    $(this).addClass('chosen');
                    $('input#id_remote_image').val($(this).attr('src'));
                    $('input#image-clear_id').prop('checked', true);
                });
            });
        });
    }());
});
