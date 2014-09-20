function changeDate(date) {
    var selectedDate = webix.Date.dateToStr("%Y-%m-%d")(date);

    var exists = "{% url 'pos_view_date_exist' %}" + selectedDate;

    webix.ajax(exists, function (response) {
        if (response == 'True') {
            var index = "{% url 'pos_view_app_index' %}" + selectedDate;
            webix.send(index, null, 'GET');
        }
        else {
            webix.message({
                type: "error",
                text: selectedDate + " date not found!"
            });
        }
    })
}

var logic = {
    init: function () {
        $$("overall").load(overall_url);

        $$("pos_calendar").attachEvent("onDateSelect", changeDate);
        $$("pos_calendar").setValue(date);

        $$("positions").load(positions_url);

        menu_init();
    }
};