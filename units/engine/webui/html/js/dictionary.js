
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
        data = {'entity':'dictionary', 'limit':this.limit, 'offset':(this.index * this.limit)};

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[dictionary.get] request error: ' + JSON.stringify());
            },

            success: function(result) {

                console.log('dictionary size: ' + result.size);

                console.log(result);

                var table = $('#dictionary-table tbody');
                table.html('');

                $.each(result.rows, function(index, row){
                    console.log('row[' + index + ']: ' + JSON.stringify(row));

                    template = '<tr>' +
                               '    <td>{{id}}</td>' +
                               '    {{#username}}' +
                               '    <td>{{username}}</td>' +
                               '    {{/username}}' +
                               '    {{^username}}' +
                               '    <td><i class="fa fa-times fa-fw"></i></td>' +
                               '    {{/username}}' +
                               '    {{#password}}' +
                               '    <td>{{password}}</td>' +
                               '    {{/password}}' +
                               '    {{^password}}' +
                               '    <td><i class="fa fa-times fa-fw"></i></td>' +
                               '    {{/password}}' +
                               '    <td></td>' +
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

    this.add_entry = function() {

        template = '<tr>' +
                   '    <td class="pair">{{username}}</td>' +
                   '    <td class="pair">{{password}}</td>' +
                   '    <td></td>' +
                   '    <td></td>' +
                   '</tr>';

        if(this.values == undefined)
            this.values = [];

        var keywords = {};
        if(!$('#null_username').prop("checked"))
            keywords.username = $('#username').val();
        else
            keywords.username = null;

        if(!$('#null_password').prop("checked"))
            keywords.password = $('#password').val();
        else
            keywords.password = null;

        if(!(('username' in keywords) || ('password' in keywords)))
            return;

        this.values.push({'dictionary':keywords});

        console.log('[dictionary.add_entry] ' + JSON.stringify(keywords));

        html = Mustache.to_html(template, keywords);

        console.log(html);

        $('#entries_table tbody').append(html);

    };

    this.add_entries = function() {

        console.log('SENDING!!!');

        if((this.values == undefined) || (this.values.length == 0))
            return;

        $.ajax({
            type: 'POST',
            url: '/api/set',
            data: JSON.stringify(this.values),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                        console.log('[ADD_TASK.RESPONSE] ' + JSON.stringify(response));
                     }
        });

        //console.log(JSON.stringify(attrs));
    };
};