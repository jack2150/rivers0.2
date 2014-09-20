var symbols_ui = {
    id: "symbols_ui",
    view: "list",
    scroll: "x",
    layout: "x",
    select: true,
    type:{
        width: 186,
        height: 114
    },
    scheme:{
        $sort: {
            by: "pl_open",
            dir: "asc",
            as: "int"
        }
    },
    template: "http->{{ STATIC_URL }}apps/pms_app/spread_view_app/symbols_ui.html"
};

var tabbar_ui = {
    // segmented, tabbar
    id: "tabbar_ui",
    view: "tabbar",
    value: "listView",
    type: "bottom",
    multiview: true,
    height: 62,
    padding: 10,
    options: [
        {value: "<i class='fa fa-tachometer'></i><div>List</div>", id: '1'},
        {value: "<i class='fa fa-anchor'></i><div>Form</div>", id: '2'},
        {value: "<i class='fa fa-calendar'></i><div>Form</div>", id: '3'},
        {value: "<i class='fa fa-money'></i><div>Form</div>", id: '4'},
        {value: "<i class='fa fa-bar-chart'></i><div>Form</div>", id: '5'},
        {value: "<i class='fa fa-check-square-o'></i><div>Form</div>", id: '6'},
        {value: "<i class='fa fa-asterisk'></i><div>Form</div>", id: '7'},
        {value: "<i class='fa fa-adjust'></i><div>Form</div>", id: '8'}
    ]
};

var cells_ui = {
    animate: false,
    cells: [
        { id: "1", template: "1" },
        { id: "2", template: "2" },
        { id: "3", template: "3" }
    ]
};

var spread_ui = { body: {
    type: 'clean',
    padding:8,
    rows: [
        {
            id: "spread_ui",
            template: "http->{{ STATIC_URL }}apps/pms_app/spread_view_app/spread_ui.html",
            height: 38
        },
        {
            type:"clean",
            padding:8,
            rows: [
                tabbar_ui,
                cells_ui
            ]
        }

    ]
}};

var ui_body = {
    view:"accordion",
    type: "space",
    cols: [
        { header:"MENU", body: menu_links },
        { type: "wide", rows: [
            spread_ui,
            symbols_ui
        ]}
    ]
};