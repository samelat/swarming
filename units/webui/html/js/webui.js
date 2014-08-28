

subunits  = new SubUnits();

messenger = new Messenger();
messenger.update = subunits.update;

main_menu = new MainMenu();

function sunit_menu() {
    messenger.start();
    $('#sunit_menu').attr('class', 'active');
    $('#dict_menu').attr('class', null);
}

function dict_menu() {
    $('#sunit_menu').attr('class', null);
    $('#dict_menu').attr('class', 'active');
}
