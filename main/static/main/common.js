const userToken = localStorage.getItem("user_token");
$.ajaxSetup({"headers": {"Authorization": userToken}});

let orderColumn = null;

//Вывод сообщений в специальное модальное окно

function showMessage(msg) {
    let $messageBlock = $("#message-block");
    showModal($messageBlock);
    $("p", $messageBlock).text(msg);
}

function showAjaxError(jqXHR, $modal = null) {
    if ($modal) {
        closeModal($modal);
    }
    let errorText;
    if ('responseText' in jqXHR) {
        if (jqXHR.status >= 500) {
            errorText = `(${jqXHR.status}. ${jqXHR.statusText}) Внутренняя ошибка сервера`;
        } else {
            let responseObj = JSON.parse(jqXHR.responseText);
            let errors = [];
            for (let key of Object.keys(responseObj)) {
                errors.push(responseObj[key]);
            }
            errorText = `(${jqXHR.status}. ${jqXHR.statusText}) ${errors.join(" ")}`;
        }
    } else {
        errorText = "Сервер не доступен...";
    }
    showMessage(errorText);
}

//Закрытие открытие модальных окон с блокировкой/разблокированием скролла страницы

function showModal($modal) {
    document.body.style.overflow = "hidden";
    $modal.show("normal");
}

function closeModal($modal) {
    document.body.style.overflow = "auto";
    $modal.hide("normal");
}

// Форматирование дат в объектах, содержащих поля dt_created и dt_updated

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

// Функции поиска объектов по заданной строке и сортировки списков объектов

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

//Функции запроса списка объектов для добавления в элемент и скролла элемента с запросом новых данных

function getDownloadListFunction($resultDiv) {
    function downloadList(url) {
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data) {
                let products = data.results;
                let nextPage = data.next;
                $resultDiv.data("nextPage", nextPage);
                if (products.length === 0) {
                    $resultDiv.append($("<span>").text("Ничего не найдено..."));
                    return;
                }
                for (let product of products) {
                    $resultDiv.append($("<p>").text(product.title).data("element", product));
                }
            },
            "error": function (jqXHR) {
                $resultDiv.slideUp("normal");
                showAjaxError(jqXHR);
            }

        })
    }

    return downloadList;
}

function getScrollListFunction(searchListFunc) {
    function scrollList() {
        let $this = $(this);
        let nextPage = $this.data("nextPage");
        if (!nextPage) return;

        let downloadTriggerValue = this.scrollHeight - (this.scrollTop + this.clientHeight);
        if (downloadTriggerValue < 50) {
            searchListFunc(nextPage);
        }
    }

    return scrollList
}
