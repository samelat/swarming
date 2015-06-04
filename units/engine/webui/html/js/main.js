
function Main () {

    this.name = 'main';

    this.entities = {
        'task':0,
        'success':0,
        'dictionary':0
    }

    this.timestamp = 0;

    this.start = function() {
        this.request([],

        function(result) {
            console.log('response: ' + JSON.stringify(result));
            module.timestamp = result.timestamp;
        });
    };
    
    this.request = function(query, action) {

        //data = {'entity':entity, 'aggregate':'count', 'conditions':{'timestamp':module.timestamp}};
        console.log('request: ' + JSON.stringify(query));

        $.ajax({
            type: 'POST',
            url: '/api/get',
            data: JSON.stringify(query),
            contentType: 'application/json',
            dataType: 'json',

            error: function() {
                console.log('[dictionary.get] request error: ' + JSON.stringify());
            },

            success: action
        });
    };

    this.update = function() {

        var query = [
            {'entity':'task',       'aggregate':'count', 'conditions':{'timestamp':module.timestamp}},
            {'entity':'success',    'aggregate':'count', 'conditions':{'timestamp':module.timestamp}},
            {'entity':'dictionary', 'aggregate':'count', 'conditions':{'timestamp':module.timestamp}}
        ];

        module.request(query, function(response) {
            console.log('response: ' + JSON.stringify(response));

            $.each(['task', 'success', 'dictionary'], function(index, value) {

                var summary = $('#'+value+'_summary .notify');

                if(!response.results[index].count)
                    summary.hide();
                else {
                    summary.text(response.results[index].count);
                    summary.show();
                }
            });
        });
    };

    this.show_summary = function(tag_name) {

        core.load(tag_name);
    };
};