
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
                    var html_row = '<tr class="odd gradeX">' +
                                        '<td>' + JSON.stringify(obj) + '</td>' +
                                        '<td>' + 'otra cosa' + '</td>' +
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