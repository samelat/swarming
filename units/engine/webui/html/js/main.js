
function Main () {

    this.name = 'main';

    this.entities = {
        'task':0,
        'success':0,
        'dictionary':0
    }

    this.timestamp = 0;

    this.start = function() {
        this.update();
    };
    
    this.new_entries = function(entity) {

        data = {'entity':entity, 'aggregate':'count', 'conditions':{'timestamp':module.timestamp}};
        console.log('request: ' + JSON.stringify(data));

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[dictionary.get] request error: ' + JSON.stringify());
            },

            success: function(result) {

                console.log('response: ' + JSON.stringify(result));
                module.timestamp = result.timestamp;
            }
        });
    };

    this.update = function() {
        module.new_entries('task');
        module.new_entries('success');
        module.new_entries('dictionary');
        //module.new_entries('task');
    };

    this.show_summary = function(tag_name) {

        core.load(tag_name);
    };
};