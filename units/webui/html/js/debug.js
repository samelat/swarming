
function Debug () {

    this.send_request_message = function() {
        var text = $('#request_area').val();
        var message = JSON.parse(text);

        console.log(text);
        console.log(message);
        
        messenger.request(message, function(response) {
            $('.response-panel').text(JSON.stringify(response));
        });
    };

    this.set_request_area = function(unit, command) {
        var message = {"dst":unit,
                       "cmd":command,
                       "params":messenger.templates[unit][command]}
        $('#request-area').val(JSON.stringify(message));
    };
}

var debug = new Debug();
