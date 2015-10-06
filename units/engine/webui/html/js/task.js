
function Task () {

    this.name = 'task';
    this.limit = 10;
    this.index = 0;

    this.start = function() {
        this.update();
    };

    this.page = function(page) {
        this.index = page;
        this.update();

        $('#task-table thead input[type="checkbox"]')[0].checked = false;
    };

    this.update = function() {
        $.ajax({
            type: 'GET',
            url: '/api/tasks',
            data: {'count': 1},

            error: function() {
                console.log('[task.update] request error');
            },

            success: function(response) {
                var count = response.result.count;
                $.ajax({
                    type: 'GET',
                    url: '/api/tasks',
                    data: {'limit':module.limit, 'offset':(module.index * module.limit)},
                    dataType: 'json',

                    error: function() {
                        console.log('[task.update_table] request error');
                    },

                    success: function(response) {

                        var rows  = response.result;
                        var table = $('#task-table tbody');
                        var table_html = '';

                        $.each(rows, function(index, row){

                            if(row.state != 'complete') {
                                row.striped = 'progress-bar-striped';
                                if(row.state == 'running')
                                    row.striped += ' active';
                            }

                            if(row.state == 'error')
                                row.progress_name = 'error';
                            else {
                                row.progress_name = row.stage.split('.')[0];
                                if(row.progress_name == 'cracking')
                                    if('complement' in row)
                                        row.lock = 'unlock';
                                    else
                                        row.lock = 'lock';
                            }

                            row.percentage = 0;
                            if(row.total > 0)
                                row.percentage = Math.round((row.done/row.total)*100);

                            if(row.state != 'complete') {
                                var cbox = $('#task_checkbox_' + row.id)[0];
                                if(cbox && cbox.checked)
                                    row.checked = 'checked="checked"';
                            } else
                                row.checked = 'disabled';

                            template = '<tr>' +
                                       '    <td><input id="task_checkbox_{{id}}" type="checkbox" {{checked}}></td>' +
                                       '    <td>{{id}}</td>' +
                                       '    <td>{{protocol}}://{{hostname}}:{{port}}{{path}}</td>' +
                                       '    <td>' +
                                       '        <div class="progress {{progress_name}}">' +
                                       '            <div class="progress-bar {{progress_name}} {{striped}}" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: {{percentage}}%">' +
                                       '                <span>{{percentage}}%</span>' +
                                       '            </div>' +
                                       '        </div>' +
                                       '    </td>' +
                                       '    <td>{{description}}</td>' +
                                       '    <td>{{stage}}</td>' +
                                       '    <td>{{state}}</td>' +
                                       '    <td>' +
                                       '    {{#dependence}}' +
                                       '        <i class="fa fa-link fa-fw" title="Task #{{dependence.id}}"></i>' +
                                       '    {{/dependence}}' +
                                       '    {{#lock}}' +
                                       '        <i class="fa fa-{{lock}} fa-fw"></i>' +
                                       '    {{/lock}}' +
                                       '    </td>' +
                                       '</tr>';

                            table_html += Mustache.to_html(template, row);
                        });

                        table.html(table_html);

                        pages = Math.ceil(count / module.limit);

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

                            $('#pagination_bar').html(html);
                        } else
                            $('#pagination_bar').html('');
                    }
                });
            }
        });
    };

    this.add_task = function() {

        var uri = $('.row input[name="uri"]').val();
        var state = $('.row select[name="state"]').val();

        // ... "http", "127.0.0.1", "9090", "/index.php", "var1=val1&var2=val2&var3=val3"]
        values = {};
        split = /([^:]+):\/\/([^:\/]+)(?::(\d+))?([^\?]+)?(?:\?([^#]+))?/i.exec(uri);
        values['protocol'] = split[1];
        values['hostname'] = split[2];

        if(split[3] != undefined)
            values['port'] = parseInt(split[3]);

        if(split[4] != undefined)
            values['path'] = split[4];

        // I have to decide how to handle this.
        // if(split[5] != undefined)
        //     values['query'] = split[5];

        values['state'] = state;

        $.ajax({
            type: 'POST',
            url: '/api/tasks',
            data: JSON.stringify(values),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                console.log('[ADD_TASK.RESPONSE] ' + JSON.stringify(response));
             }
        });

        $('#add_task_modal').modal('toggle');
    };

    this.change_state = function() {

        var state = $('select.form-control')[0].value;

        var changes = [];
        $('tbody input[type="checkbox"]').each(function(index, tag){
            if(tag.checked)
                changes.push({'task':{'id':parseInt(tag.id.split('_')[2]), 'state':state}});

            tag.checked = false;
        });

        if(changes.length)
            $.ajax({
                type: 'PUT',
                url: '/api/resources/task',
                data: JSON.stringify(changes),
                contentType: 'application/json',
                dataType: 'json',
                success: function(response) {
                    console.log('[ADD_TASK.RESPONSE] ' + JSON.stringify(response));
                 }
            });

        $('#task-table thead input[type="checkbox"]')[0].checked = false;
    };

    this.toggle_checkboxs = function(checkbox_tag) {
        var value = checkbox_tag.checked;
        $('tbody input[type="checkbox"]').each(function(index, tag){
            if(!tag.disabled)
                tag.checked = value;
        });
    };

    /*
     * Upload File Modal Methods
     */
    this.show_upload_modal = function() {
        $('#upload_task_modal .alert').hide();
        //$("#upload_form").submit(module.upload_file);
        $("#upload_task_modal").modal("toggle");
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
        params.entity = 'task';
        //params.fields = {'protocol':'protocol', 'hostname':'hostname',
        //                 'port':'port', 'path':'path', 'url':'url'};
        
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

        $("#upload_task_modal").modal("toggle");
    };

};