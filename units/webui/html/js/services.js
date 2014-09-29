
function Services () {

    this.timestamp = 0;

    this.update_services = function() {
        
        var message = messenger.get_message_template("brain", "get")
        message.params.table_name = "login";
        message.params.timestamp  = services.timestamp;

        messenger.request(message, {'response':function(response) {
                console.log("RESPONSE: " + JSON.stringify(response));
                var table_body = $('#login-table tbody').val(JSON.stringify(response));
                $.each(response.rows, function(index, obj){
                    var params = '<ul class="list-unstyled">';/*
                    $.each(obj.params, function(key, value){
                        params += '<li>' + key + '=' + value + '</li>';
                    });*/
                    params += '</ul>';

                    var attrs = '<ul class="list-unstyled">';/*
                    $.each(obj.attrs, function(key, value){
                        attrs += '<li>' + key + '=' + value + '</li>';
                    });*/
                    for(var key in obj.attrs)
                        attrs += '<li>' + key + '=' + obj.attrs[key] + '</li>';
                    attrs += '</ul>';

                    var html_row = '<tr class="odd gradeX">' +
                                        '<td>' + obj.service.protocol + '</td>' +
                                        '<td>' + obj.service.hostname + '</td>' +
                                        '<td>' + obj.service.port + '</td>' +
                                        '<td>' + obj.path + '</td>' +
                                        '<td>' + params + '</td>' +
                                        '<td>' + attrs + '</td>' +
                                        '<td>' +
                                            '<a href="javascript:alert(\'remove login\')">' +
                                                '<i class="fa fa-times fa-fw"></i>' +
                                            '</a>' +
                                        '</td>' +
                                    '</tr>';
                    table_body.append(html_row);
                });

                services.timestamp = response.timestamp;
            }
        });
    };

    this.update = function() {
        services.update_services();
    };

    this.add_login = function() {
        var message = messenger.get_message_template("brain", "add")
        message.params.table_name = "login";

        message.params.values.service = {};
        $('#newLogin .login input').each(function(index, obj) {
            message.params.values[obj.name] = obj.value;
        });
        message.params.values.params = JSON.parse(message.params.values.params);
        message.params.values.attrs = JSON.parse(message.params.values.attrs);

        $('#newLogin .service input').each(function(index, obj) {
            message.params.values.service[obj.name] = obj.value;
        });

        message.params.values.service.port = parseInt(message.params.values.service.port);

        console.log(message);

        messenger.request(message);

        $('#newLogin').modal('hide');
    };
};

var services = new Services();
messenger.update = services.update;
messenger.start();