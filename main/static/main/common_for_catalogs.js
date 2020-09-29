let orderColumn = null;

function formatDates(obj) {
    //Приводим даты к более читаемому виду
    let dateExp = /(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d:\d\d)/;
    if ("dt_created" in obj) {
        let [_, year, month, day, time] = dateExp.exec(obj.dt_created);
        obj.dt_created = `${day}.${month}.${year} ${time}`;
    }
    if ("dt_updated" in obj) {
        let [_, year, month, day, time] = dateExp.exec(obj.dt_updated);
        obj.dt_updated = `${day}.${month}.${year} ${time}`;
    }
    return obj;
}

function getSearchFunction(showFunc, $searchField = $("#search-field")) {
    function search() {
        //Формируем url для поискового запроса
        let urlForSearch;
        let searchString = $searchField.val();

        console.log();
        console.log(searchString);

        if (searchString) {
            urlForSearch = `${apiURL}?search=${searchString}`;
        } else {
            urlForSearch = apiURL;
        }

        //Удаляем старые параметры сортировки
        if (orderColumn) {
            orderColumn.column.text(orderColumn.column.attr("display-name"));
            orderColumn = null;
        }

        showFunc(urlForSearch);
    }

    return search;
}

function getSortFunction(showFunc) {
    function sort() {
        let $this = $(this);

        if (orderColumn) {
            if (orderColumn.column.attr("column-key") === $this.attr("column-key")) {
                orderColumn.order = {"+": "-", "-": "+"}[orderColumn.order]
            } else {
                orderColumn.column.text(orderColumn.column.attr("display-name"));
                orderColumn = {
                    column: $this,
                    order: orderColumn.order
                };
            }
        } else {
            orderColumn = {
                column: $this,
                order: "+"
            };
        }

        orderColumn.column.text(orderColumn.column.attr("display-name") + "(" + orderColumn.order + ")");
        let urlForRequest = apiURL + "?";
        urlForRequest += "order=" + (orderColumn.order === "+" ? "" : "-") + $this.attr("column-key");

        let searchText = $("#search-field").val();
        urlForRequest += searchText ? "&search=" + searchText : "";

        showFunc(urlForRequest);
    }

    return sort;
}