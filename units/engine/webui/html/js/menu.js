
function Menu () {

    this.sb_click = function(tag) {

        core.load(tag.name);
        
        $("#side-menu li .active").removeAttr("class");
        $(tag).addClass('active');
    };
};

var menu = new Menu();