var positions = {
    id: 1,
    value: "Position Statement",
    open: false,
    data: [
        { id:"{% url 'pos_view_app_index' %}", value: "View" },
        { id:"{% url 'pos_import_app_index' %}", value: "Import" }
    ]
};

var spreads = {
    id: 2,
    open: false,
    value: "Spreads",
    data: [
        { id:"{% url 'spread_app_index' %}", value:"View" },
        { id:"21", value:"Not Yet" }
    ]
};

links = [
    positions,
    spreads
];