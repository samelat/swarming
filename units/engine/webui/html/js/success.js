
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

        success_data = [{'entity':'success', 'aggregate':'count'},
                        {'entity':'success', 'limit':this.limit, 'offset':(this.index * this.limit)}];

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(success_data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[success.update] request error');
            },

            success: function(success_response) {

                var count = success_response.results[0].count;
                var success_rows = success_response.results[1].rows;

                console.log('COUNT: ' + count);
                console.log('SUCCESS: ' + JSON.stringify(success_rows));

                task_data = [];
                $.each(success_rows, function(index, success_row) {
                    task_data.push({'entity':'task', 'conditions':{'id':success_row.task.id}});
                });

                $.ajax({
                    type: 'POST',
                    url: '/api/get',
                    data: JSON.stringify(task_data),
                    contentType: 'application/json',
                    dataType: 'json',

                    success: function(task_response) {

                        //console.log(JSON.stringify(task_response));

                        var table = $('#success-table tbody');
                        table.html('');

                        $.each(success_rows, function(index, row){

                            console.log(row);

                            var task_row = task_response.results[index].rows[0];

                            url_html = Mustache.to_html('<td>{{protocol}}://{{hostname}}:{{port}}{{path}}</td>', task_row);

                            row.description = task_row.description;

                            template = '<tr>' +
                                       '    <td>{{id}}</td>' +
                                       '    <td>{{credentials.username}}</td>' +
                                       '    <td>{{credentials.password}}</td>' +
                                       url_html +
                                       '    <td>{{description}}</td>' +
                                       '</tr>';

                            html = Mustache.to_html(template, row);
                            table.append(html);

                        });

                        pages = Math.ceil(count / module.limit);

                        console.log('result.size: ' + count);
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
                }); // Second Ajax Request
            }
        }); // First Ajax Request
    };
};