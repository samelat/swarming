

function Debug () {

    this.send_request_message = function() {
        var text = $('#request_area').val();
        var message = JSON.parse(text);

        console.log(text);
        console.log(message);
        
        messenger.request(message, function(response) {
            $('#response_area').text(JSON.stringify(response));
        });
    };

    this.start = function() {
        messenger.update = debug.update;
        messenger.start();
    };

    this.update = function() {

    };

    this.set_request_area = function(value) {
        $('#request_area').val(JSON.stringify(value));
    };
}