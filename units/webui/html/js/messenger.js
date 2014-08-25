

function Messenger () {

    this.callbacks = {};
    this.keys = [];

    this.update = function(){};

    this.start = function(){
        window.setInterval(this.poll, 10000);
    };

    /* ########################################
     * 
     */
    this.poll = function() {
        console.log('poll');
        messenger.response();
    };

    this.request = function(message, callback) {
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
            success: function(response) {
                console.log('request success: ' + JSON.stringify(response));

                messenger.callbacks[response['channel']] = callback;
                messenger.keys.push(response['channel']);

                console.log('response channel: ' + response['channel']);
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
    }
}