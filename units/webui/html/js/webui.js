

subunits  = new SubUnits();

messenger = new Messenger();
//messenger.update = subunits.update;

main_menu = new MainMenu();

debug = new Debug();
management_menu = new ManagementMenu();

//$().ready(main_menu.show_debug_panel);
$().ready(main_menu.show_debug_panel);
