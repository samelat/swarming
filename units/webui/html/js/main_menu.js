

function MainMenu () {

    this.show_management_panel = function() {
        //$('#debug_panel').attr('hidden', true);
        //$('#manage_panel').attr('hidden', false);
        $('#management_button').attr('class', 'active')
        $('#debug_button').attr('class', '');

        $('#ui_body').load('management_panel.html', function() {
            management_menu.show_subunits_manager();
        });
    };

    this.show_debug_panel = function() {
        //$('#manage_panel').attr('hidden', true);
        //$('#debug_panel').attr('hidden', false);
        $('#debug_button').attr('class', 'active');
        $('#management_button').attr('class', '');

        $('#ui_body').load('debug_panel.html');

        debug.start();
    };
}