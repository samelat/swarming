

subunits  = new SubUnits();

messenger = new Messenger();
messenger.start();
messenger.update = subunits.update;

function sunit_menu() {
    $('#sunit_menu').attr('class', 'active');
    $('#dict_menu').attr('class', null);
}

function dict_menu() {
    $('#sunit_menu').attr('class', null);
    $('#dict_menu').attr('class', 'active');
}
