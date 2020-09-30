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

function getSearchFunction(showFunc, $searchField, baseURL) {
    function search() {
        //Формируем url для поискового запроса
        let urlForSearch;
        let searchString = $searchField.val();
        if (searchString) {
            urlForSearch = `${baseURL}?search=${searchString}`;
        } else {
            urlForSearch = baseURL;
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

function getSortFunction(showFunc, $searchField, baseURL) {
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
        let urlForRequest = baseURL + "?";
        urlForRequest += "order=" + (orderColumn.order === "+" ? "" : "-") + $this.attr("column-key");

        let searchText = $searchField.val();
        urlForRequest += searchText ? "&search=" + searchText : "";

        showFunc(urlForRequest);
    }

    return sort;
}