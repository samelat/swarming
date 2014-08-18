

subunits_handler = new SubUnits();
messenger = new Messenger();

function sunit_menu() {
    $('#sunit_menu').attr('class', 'active');
    $('#dict_menu').attr('class', null);
}

function dict_menu() {
    $('#sunit_menu').attr('class', null);
    $('#dict_menu').attr('class', 'active');
}
