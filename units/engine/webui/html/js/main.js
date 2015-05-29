
function Main () {

    this.name = 'main';

    this.new_entries = {"dictionary":0,
                        "success":0,
                        "task":0,
                        "debug":0}

    this.start = function() {
        
    };
    
    this.update = function() {

    };

    this.show_summary = function(tag_name) {

        core.load(tag_name);
    };
};