function menu_init() {
    // for different app menu links
    $$("menu_links").parse(links);

    // tree do not use sync, tree use load
    $$("menu_links").select(current_path);
    $$("menu_links").open($$("menu_links").getParentId(current_path));

    $$('menu_links').attachEvent("onAfterSelect", function() {
        //webix.message($$('menu_links').getIndexById(current_path));

        var url = $$("menu_links").getSelectedId();

        if (isNaN(url)) {
            webix.send(url, null, "GET");
        }
    })
}