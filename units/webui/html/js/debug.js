
function Debug () {

    this.send_request_message = function() {
        var text = $('#request-area').val();
        var message = JSON.parse(text);

        console.log(text);
        console.log(message);
        
        messenger.request(message, {'response':function(response) {
                console.log("RESPONSE: " + JSON.stringify(response));
                $('#response-area').val(JSON.stringify(response));
            },
            'success':function(result){
                console.log("RESULT: " + JSON.stringify(result));
                $('#response-area').val(JSON.stringify(result));
            }
        });
    };

    this.set_request_area = function(unit, command) {
        var message = messenger.get_message_template(unit, command);
        $('#request-area').val(JSON.stringify(message));
    };
}

var debug = new Debug();
