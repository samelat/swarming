
function Tasks () {

    this.timestamp = 0;

    this.update_tasks = function() {
        console.log('HOLA');
        
        var message = messenger.get_message_template("tasker", "get")
        message.params.table = "task";
        message.params.timestamp  = tasks.timestamp;

        messenger.request(message, {'response':function(response) {
                console.log("RESPONSE: " + JSON.stringify(response));
                var table_body = $('#task-table tbody').val(JSON.stringify(response));
                $.each(response.rows, function(index, obj){
                    /*
                    var params = '<ul class="list-unstyled">';
                    for(var key in obj.params)
                        params += '<li>' + key + '=' + obj.params[key] + '</li>';
                    params += '</ul>';

                    var attrs = '<ul class="list-unstyled">';
                    for(var key in obj.attrs)
                        attrs += '<li>' + key + '=' + obj.attrs[key] + '</li>';
                    attrs += '</ul>';*/

                    var html_row = '<tr class="odd gradeX">' +
                                        '<td>' + obj + '</td>' +
                                        '<td>' + obj + '</td>' +
                                        '<td>' + obj + '</td>' +
                                        '<td>' +
                                            '<div class="progress progress-striped active">' +
                                                '<div class="progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: 74%">' +
                                                '</div>' +
                                            '</div>' +
                                        '</td>' +
                                    '</tr>';
                    table_body.append(html_row);
                });

                tasks.timestamp = response.timestamp;
            }
        });
    };

    this.update = function() {
        tasks.update_tasks();
    };
    /*
    this.add_task = function() {
        var message = messenger.get_message_template("tasker", "set")
        message.params.table = "task";

        message.params.values.service = {};
        $('#newLogin .login input').each(function(index, obj) {
            message.params.values[obj.name] = obj.value;
        });
        message.params.values.params = JSON.parse(message.params.values.params);
        message.params.values.attrs = JSON.parse(message.params.values.attrs);

        $('#newLogin .service input').each(function(index, obj) {
            message.params.values.service[obj.name] = obj.value;
        });
        message.params.values.service.protocol = {'name':message.params.values.service.protocol};
        message.params.values.service.port = parseInt(message.params.values.service.port);

        console.log(message);

        messenger.request(message);

        $('#newLogin').modal('hide');
    };*/
};

var tasks = new Tasks();
messenger.update = tasks.update;
messenger.start();