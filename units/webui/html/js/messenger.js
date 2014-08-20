

function Messenger () {

    this.callbacks = {};
    this.keys = [];

    this.start = function(){
        window.setInterval(this.response, 5000);
    };

    /* ########################################
     * 
     */
    this.request = function(message, callback) {
        $.ajax({
            type: "POST",
            url: '/request',
            data: JSON.stringify(message),
            contentType: 'application/json',
            dataType: 'json',
            /*error: function() {
                alert("error");
            },*/
            success: function(response) {
                console.log("success");
                console.log(response);

                messenger.callbacks[response['id']] = callback;
                messenger.keys.push(response['id']);

                console.log(response['id']);
                //for(var i in data){
                //    alert(data[i]);
                //}
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
            /*error: function() {
                alert("error");
            },*/
            success: function(response) {
                console.log("response success");
                console.log(JSON.stringify(response));

                $.each(response['channels'], function(index, channel){
                    messenger.keys.splice(index, 1);
                });

                $.each(response['channels'], function(index, channel){
                    console.log('FROM RESPONSE!!!');
                    console.log(channel);
                    console.log(response['responses'][channel]);
                    messenger.callbacks[channel](response['responses'][channel]);
                });
            }
        });
    }
}