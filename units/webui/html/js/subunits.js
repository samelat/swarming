
function SubUnits () {
    this.sunits = {1337:{'protocol':'http',
                         'command':'bforce',
                         'hostname':'127.0.0.1',
                         'port':9090,
                         'path':'index.php',
                         'state':'running'}};
    this.timestamp = 0;

    /*
        Events that interact with the messenger.
    */
    this.update = function() {
        var message = {};

        message.dst = 'brain';
        message.cmd = 'get_sunits';
        message.params = {};
        message.params.timestamp = subunits.timestamp;
        
        messenger.request(message, function(response) {
            
            console.log('[get_sunits] request callback: ' + JSON.stringify(response));
            //var sunit = response['params']['subunit'];
            //subunits_handler.subunits[sunit.sunit_id] = sunit;
            //subunits_handler.add_subunit_row(sunit.sunit_id);
            var sunit_ids = [];
            $.each(response.sunits, function(index, sunit){
                subunits.sunits[sunit.sunit_id] = sunit;
                sunit_ids.push(sunit.sunit_id);
            });

            subunits.timestamp = response.timestamp;
            //sunit_ids = [1337];
            subunits.refresh_sunit_rows(sunit_ids);
        });
    };

    this.send_new_subunit = function() {
        var sunit = {};
        var message = {};

        var fields = $("#add_subunit_form input");
        jQuery.each(fields, function(i, field) {
            sunit[field.name] = field.value;
        });

        message.dst = 'brain';
        message.cmd = 'add_sunit';
        message.params = {};
        message.params.sunit = sunit;
        message.params.context = {};
        
        messenger.request(message, function(response) {
            console.log('[send_new_subunit] request callback: ' + JSON.stringify(response));
            //var sunit = response['params']['subunit'];
            //subunits_handler.subunits[sunit.sunit_id] = sunit;
            //subunits_handler.add_subunit_row(sunit.sunit_id);
        });
    }

    /*
        Here we are going to put all the function to
        use to modify the subunits page.
    */
    this.refresh_sunit_rows = function(sunit_ids) {

        console.log('############################################');
        console.log('sunit to update: ' + sunit_ids);
        console.log(JSON.stringify(subunits.sunits));
        console.log('############################################');
        $.each(sunit_ids, function(index, sunit_id) {
            var sunit = subunits.sunits[sunit_id];
            var sunit_html = '<td>' + sunit.protocol + '</td>\
                                <td>' + sunit.command  + '</td>\
                                <td>' + sunit.hostname + ':' + sunit.port + '</td>\
                                <td>' + sunit.path     + '</td>\
                                <td>' + sunit.state    + '</td>\
                                <td>\
                                    <button type="button" class="btn btn-default btn-xs" onclick="remove_subunit()">\
                                        <span class="glyphicon glyphicon-remove"></span>\
                                    </button>\
                                    <button type="button" class="btn btn-default btn-xs" onclick="refresh_subunit()">\
                                        <span class="glyphicon glyphicon-refresh"></span>\
                                    </button>\
                                </td>';
            var sunit_tag = $('#sunit_' + sunit_id);
            if(sunit_tag.length > 0) {
                sunit_tag.html(sunit_html);
            } else {
                sunit_html = '<tr id="sunit_' + sunit_id + '">' + sunit_html + '</tr>';
                $('#sunits_list').append(sunit_html);
            }
            //
            //console.log('refresing units html');
            //console.log(.html());
        });
    };
}