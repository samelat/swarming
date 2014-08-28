

function ManagementMenu () {

    this.show_subunits_manager = function() {
        $('#subunits_tab').attr('class', 'active')
        $('#dictionaries_tab').attr('class', '');

        $('#manager_body').load('subunits_manager.html');

        subunits.start();
    };

    this.show_dictionaries_manager = function() {
        $('#dictionaries_tab').attr('class', 'active');
        $('#subunits_tab').attr('class', '')

        $('#manager_body').load('dictionaries_manager.html');
    };
};