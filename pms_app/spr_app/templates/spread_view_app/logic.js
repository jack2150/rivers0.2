function spread_json(url, symbol) {
    return url.replace(
        '_symbol_', symbol
    );
}

var logic = {
    init: function () {
        // load symbol list data

        $$("symbols_ui").load(symbols_json);

        // on symbol click, change spread ui
        $$("symbols_ui").attachEvent("onAfterSelect", function() {
            $$("spread_ui").load(spread_json(
                spread_url, $$("symbols_ui").getSelectedId().toLowerCase()
            ));
        });

        // set worst symbol as default spread ui symbol
        $$("spread_ui").load(spread_json(
                spread_url, worst_symbol
        ));
        //$$("symbols_ui").select(worst_symbol);
        $$("tabbar_ui").setValue(1);



        // menu
        menu_init();
    }
};
