
function Core () {

    this.interval_id = null;
    this.modules = {'main':Main, 'task':Task, 'dictionary':Dictionary, 'debug':Debug, 'successes':Successes};

    this.start = function(){
        this.load('main');

        this.interval_id = window.setInterval(function(){
            module.update();
        }, 16000);
    };

    this.load = function(name) {

        if(!(name in this.modules))
            name = 'main';

        $.ajax({
            type: "get",
            url: name + '.html',
            error: function() {
                console.log('[app.core] Page not found: ' + name + '.html');
            },
            success: function(result) {
                
                $('#page-wrapper').html(result);
                //console.log('response :' + result);
            }
        });

        module = new this.modules[name]();
        module.start();
    };
};

var module = null;

var core = new Core();
core.start();