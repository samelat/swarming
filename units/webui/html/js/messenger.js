

function Messenger () {

    this.templates = {
        'brain':{'add':{"table_name":"", "values":{}},
                 'get':{"table_name":null}},
        'core' :{'schedule':{}},
        'http' :{'digest':{}}
    };

    this.callbacks = {};
    this.keys = [];
    this.interval_id = 0;

    this.update = function(){};

    this.start = function(){
        if(messenger.interval_id == 0)
            messenger.interval_id = window.setInterval(this.poll, 10000);
    };

    this.stop = function() {
        if(messenger.interval_id != 0) {
            clearInterval(messenger.interval_id);
            messenger.interval_id = 0;
        }
    };

    this.get_message_template = function(unit, command){
        return {"dst":unit + ":0",
                "cmd":command,
                "params":messenger.templates[unit][command]};
    };

    /* ########################################
     * 
     */
    this.poll = function() {
        console.log('################ <poll> ################');
        messenger.response();
    };

    this.request = function(message, callbacks) {
        console.log('Request Message: ' + JSON.stringify(message));
        $.ajax({
            type: "POST",
            url: '/request',
            data: JSON.stringify(message),
            contentType: 'application/json',
            dataType: 'json',
            error: function() {
                console.log('request error');
            },
            success: function(result) {
                console.log('request result: ' + JSON.stringify(result));

                console.log("CALLBACKS!!!: " + callbacks);
                if('response' in callbacks) {
                    console.log("No deberia estar aca :S");
                    messenger.callbacks[result['channel']] = callbacks.response;
                    messenger.keys.push(result['channel']);
                }
                /*

                if('success' in callbacks)
                    callbacks.success(result);*/

                console.log('response channel: ' + result['channel']);
            }
        });
    };

    this.response = function() {
        //console.log(Object.keys(messenger.responses));
        $.ajax({
            type: "POST",
            url: '/response',
            data: JSON.stringify({'channels': messenger.keys}),
            contentType: 'application/json',
            dataType: 'json',
            error: function() {
                console.log("response error");
            },
            success: function(response) {
                console.log('response success: ' + JSON.stringify(response));
                console.log('before messenger.keys: ' + JSON.stringify(messenger.keys));
                messenger.keys = messenger.keys.filter(function(c){
                    return response['channels'].indexOf(c) < 0;
                });
                console.log('after messenger.keys: ' + JSON.stringify(messenger.keys));
                
                $.each(response['responses'], function(channel, _response){
                    console.log('calling callback for channel ' + channel);
                    messenger.callbacks[channel](_response);
                });

                messenger.update();
            }
        });
    };
};

var messenger = new Messenger();

