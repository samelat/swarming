

function Messenger () {

    this.responses = {};

    this.start = function(){
        window.setInterval(this.response, 1000);
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
                alert("success");
                alert(JSON.stringify(response))

                messenger.responses[response['id']] = callback;

                //for(var i in data){
                //    alert(data[i]);
                //}
            }
        });
    };

    this.response = function() {
        alert(this.responses.keys());
        $.ajax({
            type: "POST",
            url: '/response',
            data: JSON.stringify({'channel_ids':1}),
            contentType: 'application/json',
            dataType: 'json',
            /*error: function() {
                alert("error");
            },*/
            success: function(response) {
                //alert("responses success");
                alert(JSON.stringify(response))

                for(var index in response['responses']){
                    alert(JSON.stringify(response['responses'][index]));
                }
            }
        });

    }
}