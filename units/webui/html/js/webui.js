

subunits_handler = new SubUnits();
messenger = new Messenger();
console.log(messenger.responses.keys());
messenger.start();

function sunit_menu() {
    $('#sunit_menu').attr('class', 'active');
    $('#dict_menu').attr('class', null);
}

function dict_menu() {
    $('#sunit_menu').attr('class', null);
    $('#dict_menu').attr('class', 'active');
}
