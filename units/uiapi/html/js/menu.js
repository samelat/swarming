
function Menu () {

    this.sb_click = function(tag) {

        core.load(tag.name);

        $(tag).addClass('active');
    };
};

var menu = new Menu();