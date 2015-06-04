
function Dictionary () {

    this.name = 'dictionary';
    this.limit = 10;
    this.index = 0;

    this.start = function() {

        this.update();
    };

    this.page = function(page) {
        this.index = page;
        this.update();
    };

    this.update = function() {
        
        data = [{'entity':'dictionary', 'aggregate':'count'},
                {'entity':'dictionary', 'limit':this.limit, 'offset':(this.index * this.limit)}];

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

                    template = '<tr>' +
                               '    <td>{{id}}</td>';

                    if(row.username != null)
                        template += '    <td>{{username}}</td>';
                    else
                        template += '    <td><i class="fa fa-times fa-fw"></i></td>';

                    if(row.password != null)
                        template += '    <td>{{password}}</td>';
                    else
                        template += '    <td><i class="fa fa-times fa-fw"></i></td>';

                    template += '    <td></td>' +
                                '</tr>';

                    html = Mustache.to_html(template, row);
                    table.append(html);
                });

                pages = Math.ceil(count / module.limit);

                console.log('module.limit: ' + module.limit);
                console.log('module.index: ' + module.index);
                if(count > module.limit) {

                    template = '<ul class="pagination no-padding">' +
                               '    <li{{{left_class}}}><a onclick="module.page({{bottom}})">&laquo;</a></li>';

                    for(page=0; page < pages; page++) {
                        v = {'page':page};
                        if(page == module.index)
                            v.state = ' class="active"';

                        template += Mustache.to_html('    <li{{{state}}}><a onclick="module.page({{page}})">{{page}}</a></li>', v);
                    }

                    template += '    <li{{{right_class}}}><a onclick="module.page({{top}})">&raquo;</a></li>' +
                                '</ul>';

                    v = {'bottom':0, 'top':(pages - 1)};
                    if(module.index == 0)
                        v.left_class = ' class="disabled"';
                    else
                        v.bottom = module.index - 1;

                    if(module.index >= (pages - 1))
                        v.right_class = ' class="disabled"';
                    else
                        v.top = module.index + 1;

                    var html = Mustache.to_html(template, v);
                    console.log(html);

                    $('#pagination_bar').html(html);
                } else
                    $('#pagination_bar').html('');
            }
        });
    };

    this.add_entry = function() {

        var keywords = {"username":null, "password":null};
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
};