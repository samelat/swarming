

function Messenger () {

    this.responses = {};

    this.request = function(message) {
        alert(1);

        var jqxhr = $.getJSON( "/request", function(data) {
            alert(JSON.stringify(data));
            for(var i in data) {
                alert(i);
            }
        });
        /*
          .done(function() {
            console.log( "second success!!!" );
          })
          .fail(function() {
            console.log( "error!!!" );
          })
          .always(function() {
            console.log( "complete!!!" );
          });
         
        // Perform other work here ...
         
        // Set another completion function for the request above
        jqxhr.complete(function() {
          console.log( "second complete!!!" );
        });*/
        alert(2);
    };

}