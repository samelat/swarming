

subunits_handler = new SubUnits();
messenger = new Messenger();
//var aaa = {'a':1};
//console.log(Object.keys(aaa));
messenger.start();

function sunit_menu() {
    $('#sunit_menu').attr('class', 'active');
    $('#dict_menu').attr('class', null);
}

function dict_menu() {
    $('#sunit_menu').attr('class', null);
    $('#dict_menu').attr('class', 'active');
}
