var pos_file_header = {
    type: "header",
    template: "Import Files",
    autoheight: true
};

var pos_file_tree = {
    id: "pos_file_tree",
    view: "tree",
    activeTitle: true,
    autoheight: true,
    select:true
};

var import_button = {
    cols: [
        {
            id: "import_button",
            view:"button",
            value:"Import",
            container:"pos_file_tree",
            width: 100
        },
        { template: "" }
    ]
};



var ui_body = {
    view:"accordion",
    rows: [{
        type: "space",
        cols: [
            { header:"MENU", body: menu_links },
            { type: "line", rows: [
                pos_file_header,
                pos_file_tree,
                import_button
            ] }
        ]
    }]
};
