$(document).ready(function($) {
    'use strict';

    (function() {
        // text field filter
        var url = new URI();

        $('.admin-text-field-filter-ul').each(function() {
            var input = $(this).find('.admin-text-field-filter-input');
            var button = $(this).find('.admin-text-field-filter-button');
            var param = button.attr('data-param');
            var search = url.search(true);
            var params = {};
            var go = function() {
                var val = input.val();
                if (!val) {
                    url.removeSearch(param);
                } else {
                    params[param] = val;
                    url.setSearch(params);
                }
                location.replace(url.toString());
            };
            if (search[param]) {
                input.val(search[param]);
            }

            input.on('keyup', function(e) {
                if (e.keyCode == 13) {
                    go();
                }
            });

            button.click(go);
        });
    }());
});
