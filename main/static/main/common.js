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

//Создание обработчика для кнопок перехода на следующую и предыдущую страницы

function createPaginationButtons(prevPage, nextPage, showFunc) {
    let $prevPageButton = $("#prev-page-button");
    if (prevPage) {
        $prevPageButton.show();
        $prevPageButton.off();
        $prevPageButton.click(() => {
            showFunc(prevPage);
        })
    } else {
        $prevPageButton.hide();
    }

    let $nextPageButton = $("#next-page-button");
    if (nextPage) {
        $nextPageButton.show();
        $nextPageButton.off();
        $nextPageButton.click(() => {
            showFunc(nextPage);
        })
    } else {
        $nextPageButton.hide();
    }
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

// Проверка корректного указания количества

function checkCountValue($countField) {
    //Проверяем корректность внесения данных
    let countValue = $countField.val().trim();
    if (countValue.length === 0) {
        throw new Error("Количество не может быть пустым!");
    }
    if (!/^\d+$/.test(countValue)) {
        throw new Error("Поле заполнено некорректно!");
    }
    countValue = new Number(countValue);
    if (countValue <= 0) {
        throw new Error("Количество должно быть целым положительным числом!")
    }
}

// Функции для реализации сортировки и поиска

function getDefaultSearchParams() {
    let searchText = $("#search-field").val();
    return searchText ? `search=${searchText}` : "";
}

function getSearchFunction(showFunc, getSearchParams, baseURL) {
    function search() {
        //Формируем url для поискового запроса
        let urlForSearch;
        let searchParams = getSearchParams();
        if (searchParams) {
            urlForSearch = `${baseURL}?${searchParams}`;
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

function getSortFunction(showFunc, getSearchParams, baseURL) {
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

        let searchParams = getSearchParams();
        urlForRequest += searchParams ? `&${searchParams}` : "";

        console.log(urlForRequest);

        showFunc(urlForRequest);
    }

    return sort;
}

//Функции для реализации поиска с выводом результатов в предназначенный для этого div

function getDownloadListFunction($resultDiv, titleFieldName = "title") {
    function downloadList(url) {
        $.ajax(url, {
            "method": "GET",
            "dataType": "json",
            "success": function (data) {
                let elements = data.results;
                let nextPage = data.next;
                $resultDiv.data("nextPage", nextPage);
                if (elements.length === 0) {
                    $resultDiv.append($("<span>").text("Ничего не найдено..."));
                    return;
                }
                for (let element of elements) {
                    $resultDiv.append($("<p>").text(element[titleFieldName]).data("element", element));
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
