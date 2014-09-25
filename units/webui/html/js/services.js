
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
                    var uri = obj.service.protocol + '://' +
                              obj.service.hostname + ':' +
                              obj.service.port + '/' +
                              obj.path
                    var pairs = [];
                    $.each(obj.params, function(key, value){
                        pairs.push(key + '=' + value);
                    });

                    var params = pairs.join('&');
                    if(params)
                        uri += '?' + params

                    var html_row = '<tr class="odd gradeX">' +
                                        '<td>' + uri + '</td>' +
                                        '<td>' + JSON.stringify(obj.attrs) + '</td>' +
                                        '<td>' + 'algo mas' + '</td>' +
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
};

var services = new Services();
messenger.update = services.update;
messenger.start();