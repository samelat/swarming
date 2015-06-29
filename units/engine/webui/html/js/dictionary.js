
function Dictionary () {

    this.name = 'dictionary';
    this.elements_per_page = 10;
    this.pagination_size = 20; // Pagies
    this.pagination_index = 0;

    this.start = function() {
        this.update();
    };

    this.page = function(page) {
        this.pagination_index = page;
        this.update();
    };

    this.update = function() {
        
        data = [{'entity':'dictionary', 'aggregate':'count'},
                {'entity':'dictionary', 'limit':this.elements_per_page,
                 'offset':(this.pagination_index * this.elements_per_page)}];

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[dictionary.get] request error: ' + JSON.stringify());
            },

            success: function(response) {

                var count = response.results[0].count;
                var rows  = response.results[1].rows;

                console.log('count: ' + count);
                console.log(rows);

                var table = $('#dictionary-table tbody');
                table.html('');

                $.each(rows, function(index, row){
                    console.log('row[' + index + ']: ' + JSON.stringify(row));
                    if('charsets' in row)
                        row.charsets_json = JSON.stringify(row.charsets);
                    else
                        row.charsets_json = '';

                    template = '<tr>' +
                               '    <td>{{id}}</td>' +
                               '    <td>{{type}}</td>' ;

                    if(row.username != null)
                        template += '    <td>{{username}}</td>';
                    else
                        template += '    <td><i class="fa fa-times fa-fw"></i></td>';

                    if(row.password != null)
                        template += '    <td>{{password}}</td>';
                    else
                        template += '    <td><i class="fa fa-times fa-fw"></i></td>';

                    template += '    <td>{{charsets_json}}</td>' +
                                '    <td>{{weight}}</td>' +
                                '    <td>{{task}}</td>' +
                                '</tr>';

                    html = Mustache.to_html(template, row);
                    table.append(html);
                });

                pages = Math.ceil(count / module.elements_per_page);

                if(pages > 1) {

                    //template = '<ul class="pagination no-padding">' +
                    template = '    <li{{{left_class}}}><a onclick="module.page(0)">&laquo;</a></li>' +
                               '    <li{{{left_class}}}><a onclick="module.page({{prev}})">&lsaquo;</a></li>';

                    //pages = 20;

                    var first = module.pagination_index - (module.pagination_size / 2);
                    var last  = module.pagination_index + (module.pagination_size / 2);

                    if(first < 0) {
                        last += first * -1; // I'm moving the underflow to "last".
                        first = 0;
                    }

                    if(last >= pages)
                        last = pages - 1; // I'm ignoring any overflow.

                    for(page=first; page <= last; page++) {
                        v = {'page':page};
                        if(page == module.pagination_index)
                            v.state = ' class="active"';

                        template += Mustache.to_html('    <li{{{state}}}><a onclick="module.page({{page}})">{{page}}</a></li>', v);
                    }

                    template += '    <li{{{right_class}}}><a onclick="module.page({{next}})">&rsaquo;</a></li>' +
                                '    <li{{{right_class}}}><a onclick="module.page({{top}})">&raquo;</a></li>';
                                //'</ul>';

                    v = {'top':(pages - 1),
                         'prev':(module.pagination_index - 1),
                         'next':(module.pagination_index + 1)};
                    if(module.pagination_index == 0)
                        v.left_class = ' class="disabled"';

                    if(module.pagination_index == (pages - 1))
                        v.right_class = ' class="disabled"';

                    var html = Mustache.to_html(template, v);
                    console.log(html);

                    $('#pagination_bar').html(html);
                    $('#pagination_bar').rPage();
                } else
                    $('#pagination_bar').html('');
            }
        });
    };

    this.add_entry = function() {

        var keywords = {};
        if($("#username_radio").prop("checked"))
            keywords.username = $('#username').val();

        else if($('#password_radio').prop("checked"))
            keywords.password = $('#password').val();

        else {
            keywords.username = $('#username').val();
            keywords.password = $('#password').val();
        }

        $.ajax({
            type: 'POST',
            url: '/api/set',
            data: JSON.stringify([{'dictionary':keywords}]),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                console.log('[ADD_TASK.RESPONSE] ' + JSON.stringify(response));
            }
        });
    };

    /*
     * Upload File Modal Methods
     */
    this.show_upload_modal = function() {
        $('#upload_dictionary_modal .alert').hide();
        //$("#upload_form").submit(module.upload_file);
        $("#upload_dictionary_modal").modal("toggle");
    };

    this.change_file_format = function(tag) {
        if(tag.value == "custom")
            $("#file_regex").prop("disabled", false);
        else
            $("#file_regex").prop("disabled", true);
    };

    this.upload_file = function() {

        var alert_box = $('#upload_dictionary_modal .alert');
        var error_tmp = '<span class="fa fa-exclamation-circle" aria-hidden="true"></span>';

        var file = $('#dictionary_file')[0].files[0];
        if(file == undefined) {
            alert_box.html(error_tmp + "You haven't specified a File");
            alert_box.show();
            return false;
        }
        
        var params = {};
        params.format = $('#file_type')[0].value;
        if(params.format == 'custom') {
            var regex = $('#file_regex')[0].value;
            if(regex == "") {
                alert_box.html(error_tmp + "You haven't specified a Regex");
                alert_box.show();
                return false;
            }

            params.regex = regex;
        }

        // <table_name> => {<table_field> : <how_to_identify_it>, ...}
        params.entity = 'dictionary'
        //params.fields = {'username':'username', 'password':'password'};
        
        var data = new FormData();
        data.append('file', file);
        data.append('json_params', JSON.stringify(params));
        
        $.ajax({
            type: 'POST',
            url: '/api/upload',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log('File Upload Success.');
            },
            error: function() {
                
            }
        });

        $("#upload_dictionary_modal").modal("toggle");
    };

    this.add_charset = function() {

        var entry = '<tr>';
        entry += '<td>' + $("#mask_token")[0].value + '</td>';
        entry += '<td>' + $("#mask_value")[0].value + '</td>';
        entry += '</tr>';

        $("#charsets_table tbody").append(entry);
    };
};