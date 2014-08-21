
function SubUnits () {
    this.subunits = {1337:{'protocol':'http',
                            'command':'bforce',
                            'hostname':'127.0.0.1',
                            'port':9090,
                            'path':'index.php',
                            'state':'running'}};

    /*
        Events that interact with the messenger.
    */
    this.send_new_subunit = function() {
        var subunit = {};
        var message = {};

        var fields = $("#add_subunit_form input");
        jQuery.each(fields, function(i, field) {
            subunit[field.name] = field.value;
        });

        message['dst'] = 'brain';
        message['cmd'] = 'add_sunits';
        message['params'] = {};
        message['params']['subunit'] = subunit;
        message['params']['context'] = '';
        
        messenger.request(message, function(response) {
            //var sunit = response['params']['subunit'];
            //subunits_handler.subunits[sunit.sunit_id] = sunit;
            //subunits_handler.add_subunit_row(sunit.sunit_id);
        });
    }

    /*
        Here we are going to put all the function to
        use to modify the subunits page.
    */
    this.add_subunit_row = function(subunit_id) {
        var subunit = this.subunits[subunit_id];
        $("#subunits_list").append('<tr>\
                                        <td>' + subunit.protocol + '</td>\
                                        <td>' + subunit.command  + '</td>\
                                        <td>' + subunit.hostname + ':' + subunit.port + '</td>\
                                        <td>' + subunit.path     + '</td>\
                                        <td>' + subunit.state    + '</td>\
                                        <td>\
                                            <button type="button" class="btn btn-default btn-xs" onclick="remove_subunit()">\
                                                <span class="glyphicon glyphicon-remove"></span>\
                                            </button>\
                                            <button type="button" class="btn btn-default btn-xs" onclick="refresh_subunit()">\
                                                <span class="glyphicon glyphicon-refresh"></span>\
                                            </button>\
                                        </td>\
                                    </tr>');

    };

    this.remove_subunit = function(subunit_id) {

    };
}