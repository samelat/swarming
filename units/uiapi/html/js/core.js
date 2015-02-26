
function Core () {

    this.load = function(tag) {

        $.ajax({
            type: "get",
            url: tag.name + '.html',
            error: function() {
                console.log('[app.core] Page not found: ' + tag.name + '.html');
            },
            success: function(result) {
                
                $('#page-wrapper').html(result);
                console.log('response :' + result);
            }
        });

        tag.addClass("active");
    }
};

var core = new Core();