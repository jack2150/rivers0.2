function page(data) {
    var result = "";

    if (data.date) {
        result = "" +
            "<p id='date_path' align='center'>" +
            "Date: " + data.date + " " +
            "Filename:  " + data.fname + " " +
            "<p align='center'>" +
            "File above have saved into database." +
            "</p>";
    }
    else {
        result = "" +
            "<p align='center'>" +
            "File not found or fail save into database!" +
            "</p>";
    }

    return result
}

function complete(text, data) {
    webix.alert({
            title: "Import Completed",
            text: page(data.json()),
            width: "500px",
            callback: function() {
                var url = "{% url 'pos_import_app_index' %}";
                webix.send(url, null, "GET");
            }
        }
    );
}

var logic = {
    init: function() {
        $$('import_button').attachEvent("onItemClick", function(){
            var file_date = $$('pos_file_tree').getSelectedId();
            if (file_date != '-1' && file_date) {
                var url = "{% url 'pos_import_app_complete' %}" + file_date + "/";
                webix.ajax(
                    url,
                    complete
                );
            }
            else {
                webix.message({
                    type: "error",
                    text: "Please select file to import!"
                });
            }
        });

        // tree do not use sync, tree use load
        $$("pos_file_tree").load("{% url 'pos_import_files_json' %}");

        // menu
        menu_init();
    }
};