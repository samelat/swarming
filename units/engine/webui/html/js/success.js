
function Success () {

    this.name = 'success';
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

        data = {'entity':'success', 'limit':this.limit, 'offset':(this.index * this.limit)};

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[success.update] request error');
            },

            success: function(result) {

                console.log('success size: ' + result.size);

                var table = $('#success-table tbody');
                table.html('');

                $.each(result.rows, function(index, row){
                    console.log('row[' + index + ']: ' + JSON.stringify(row));

                    if(row.task.stage == 'forcing.dictionary') {
                        template = 'Username: "{{username}}" - Password: "{{password}}"';
                        row.credentials = Mustache.to_html(template, row.credentials);
                    }

                    template = '<tr>' +
                               '    <td>{{id}}</td>' +
                               '    <td>{{credentials}}</td>' +
                               '    <td>{{task.id}}</td>' +
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
};