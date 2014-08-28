

function MainMenu () {

    alert("cargo");

    this.select_manager = function() {
        $('#debug').attr("hidden", true);
        $('#manager').attr("hidden", false);
    };

    this.select_debug = function() {
        $('#manager').attr("hidden", true);
        $('#debug').attr("hidden", false);
    };
}