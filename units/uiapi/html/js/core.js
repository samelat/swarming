
function Core () {

    this.module = null;
    this.modules = {'main':Main, 'tasks':Tasks};

    this.load = function(tag) {

        $.ajax({
            type: "get",
            url: tag.name + '.html',
            error: function() {
                console.log('[app.core] Page not found: ' + tag.name + '.html');
            },
            success: function(result) {
                
                $('#page-wrapper').html(result);
                //console.log('response :' + result);
            }
        });

        $(tag).addClass('active');
        //alert(JSON.stringify(this.modules));
        //this.module = new this.modules[tag.name]();
        //this.module.start();
    };
};

var core = new Core();
main = $('#side-menu li a[name="main"]');
//alert(main.get(0));
core.load(main);