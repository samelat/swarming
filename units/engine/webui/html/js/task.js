
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
    };

    this.update = function() {

        data = {'entity':'task', 'limit':this.limit, 'offset':(this.index * this.limit)};

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[task.update] request error');
            },

            success: function(result) {

                console.log('task size: ' + result.size);

                var table = $('#task-table tbody');
                table.html('');

                $.each(result.rows, function(index, row){
                    console.log('row[' + index + ']: ' + JSON.stringify(row));

                    if(row.state != 'complete') {
                        row.striped = 'progress-bar-striped';
                        if(row.state == 'running')
                            row.striped += ' active';
                    }

                    row.stage_name = row.stage.split('.')[0];

                    template = '<tr>' +
                               '    <td>{{id}}</td>' +
                               '    <td>{{protocol}}://{{hostname}}:{{port}}{{path}}</td>' +
                               '    <td>' +
                               '        <div class="progress {{stage_name}}">' +
                               '            <div class="progress-bar {{stage_name}} {{striped}}" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: 74%">' +
                               '            </div>' +
                               '        </div>' +
                               '    </td>' +
                               '    <td>{{stage}}</td>' +
                               '    <td>{{state}}</td>' +
                               '    <td></td>' +
                               '</tr>';

                    html = Mustache.to_html(template, row);
                    table.append(html);
                });

                pages = Math.ceil(result.size / module.limit);

                console.log('result.size: ' + result.size);
                console.log('module.limit: ' + module.limit);
                console.log('module.index: ' + module.index);
                if(result.size > module.limit) {

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

    this.add_attr = function() {

        template = '<tr>' +
                   '    <td class="pair">{"{{key}}":{{value}}}</td>' +
                   '    <td></td>' +
                   '</tr>';

        var key = $('.row input[name="key"]').val();
        var value = $('.row input[name="value"]').val();

        if((key.length == 0) || (value.length == 0))
            return;

        html = Mustache.to_html(template, {"key":key, "value":value});

        $('#attr_table tbody').append(html);
    };

    this.add_task = function() {

        var attrs = {};
        $('#attr_table tbody .pair').each(function(index, tag){
            var tmp = JSON.parse(tag.innerText);
            $.extend(attrs, tmp);
        });

        var uri = $('.row input[name="uri"]').val();
        var state = $('.row select[name="state"]').val();
        var stage = $('.row select[name="stage"]').val();

        // ... "http", "127.0.0.1", "9090", "/index.php", "var1=val1&var2=val2&var3=val3"]
        values = {};
        split = /([^:]+):\/\/([^:\/]+)(?::(\d+))?([^\?]+)?(?:\?([^#]+))?/i.exec(uri);
        values['protocol'] = split[1];
        values['hostname'] = split[2];

        if(split[3] != undefined)
            values['port'] = parseInt(split[3]);

        if(split[4] != undefined)
            values['path'] = split[4];

        if(split[5] != undefined)
            attrs['query'] = split[5];

        values['stage'] = stage;
        values['state'] = state;

        $.ajax({
            type: 'POST',
            url: '/api/set',
            data: JSON.stringify([{'task':values}]),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                        console.log('[ADD_TASK.RESPONSE] ' + JSON.stringify(response));
                     }
        });

        //console.log(JSON.stringify(attrs));
    };
};