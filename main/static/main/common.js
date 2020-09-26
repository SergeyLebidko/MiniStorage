const userToken = localStorage.getItem("user_token");
$.ajaxSetup({"headers": {"Authorization": userToken}});


function showModal($modal) {
    document.body.style.overflow = "hidden";
    $modal.show("normal");
}

function closeModal($modal) {
    document.body.style.overflow = "auto";
    $modal.hide("normal");
}

function createErrorText(jqXHR) {
    if ('responseText' in jqXHR) {
        if (jqXHR.status >= 500) {
            return `(${jqXHR.status}. ${jqXHR.statusText}) Внутренняя ошибка сервера`;
        } else {
            let responseObj = JSON.parse(jqXHR.responseText);
            let errors = [];
            for (let key of Object.keys(responseObj)) {
                errors.push(responseObj[key]);
            }
            return `(${jqXHR.status}. ${jqXHR.statusText}) ${errors.join(" ")}`;
        }
    }
    return "Сервер не доступен..."
}