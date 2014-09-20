function numCommas(x) {
    x = Number(x).toFixed(2);
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function quantity(num) {
    return (num == 0 ? "-" : (num > 0 ? '+' + num : num))
}

function dayToExpire(num) {
    return (num == 0 ? "-" : num)
}

function floatColumn(num) {
    num = Number(num).toFixed(2);
    return (num == 0 ? "-" : (num > 0 ? '+' + num : num))
}

function percentColumn(num) {
    num = Number(num).toFixed(2);
    return (num == 0 ? "-" : (num > 0 ? '+' + num + "%" : num + "%"))
}

function bpEffect(num){
    return (num == 0 ? "-" : (num > 0 ? numCommas(num) : "(" + numCommas(-num) + ")"))
}

function no_weekend(date) {
    var result = false;
    // disable sunday and saturday
    if (date.getDay() == 0 || date.getDay() == 6)
        result = true;

    return result;
}
// Calendar Section
var pos_calendar = {
    id: "pos_calendar",
    view: "calendar",
    weekHeader: true,
    events: webix.Date.isHoliday,
    calendarDateFormat: "%Y-%m-%d",
    width: 260,
    blockDates: no_weekend
};
// Overall Section
var overall = {
    id: "overall",
    view: "property",
    editable: false,
    autoheight: true,
    width: 260,
    elements:[
        { label: "OVERALL", type: "label" },
        { label: "Date", type: "text", id: "date", format: webix.i18n.dateFormatStr },
        { label: "Cash Sweep", type: "text", id: "cash_sweep", format: bpEffect },
        { label: "P/L YTD", type: "text", id: "pl_ytd", format: bpEffect },
        { label: "BP Adjust", type: "text", id: "bp_adjust", format: bpEffect },
        { label: "Futures BP", type: "text", id: "futures_bp", format: bpEffect },
        { label: "Available $", type: "text", id: "available", format: bpEffect },
        //{ label: "CALENDAR", type: "label" },
    ]
};

var positions = {
    id: "positions",
    view: "treetable",
    columnWidth: 80,
    columns: [
        { id:"name", header:{text:"Name", css: "left"}, fillspace:true, sort:"string",
            template:"{common.treetable()} #value#", css: "left" },
        { id:"quantity", header:"Qty", width: 60, sort:"int", format:quantity },
        { id:"days", header:"Days", sort:"int", format:dayToExpire  },
        { id:"trade_price", header:"Trade Price", format:floatColumn, sort:"int" },
        { id:"mark", header:"Mark", sort:"int", format:floatColumn },
        { id:"mark_change", header:"M Chg", format:floatColumn, sort:"int" },
        { id:"delta", header:"Delta", sort:"int", format:floatColumn, footer:{ content:"summColumn" } },
        { id:"gamma", header:"Gamma", sort:"int", format:floatColumn, footer:{ content:"summColumn" } },
        { id:"theta", header:"Theta", sort:"int", format:floatColumn, footer:{ content:"summColumn" } },
        { id:"vega", header:"Vega", sort:"int", format:floatColumn, footer:{ content:"summColumn" } },
        { id:"pct_change", header:"% Change", format:percentColumn, sort:"int" },
        { id:"pl_open", header:"P/L Open", format:floatColumn, sort:"int", footer:{ content:"summColumn" } },
        { id:"pl_day", header:"P/L Day", format:floatColumn, sort:'int', footer:{ content:"summColumn" } },
        { id:"bp_effect", header:"BP EFT", width: 100, format:bpEffect,
            sort:'int', footer:{ content:"summColumn" }}
    ],
    css:"my_style",
    footer:true,
    scrollY: true,
    scrollX: true
};

var ui_body = {
    view:"accordion",
    rows: [{
        type: "space",
        cols: [
            { header:"MENU", body: {
                rows: [
                    menu_links,
                    pos_calendar,
                    overall
                ],
                type: "line"
            }},
            { body: positions }
        ]
    }]

};