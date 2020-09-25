const userToken = localStorage.getItem("user_token");
$.ajaxSetup({"headers": {"Authorization": userToken}});


function showModal($modal) {
    document.body.style.overflow = "hidden";
    $modal.show();
}

function closeModal($modal) {
    document.body.style.overflow = "auto";
    $modal.hide();
}

function createErrorText(jqXHR){
    if ('responseText' in jqXHR){
        let responseObj = JSON.parse(jqXHR.responseText);
        let errors = [];
        for (let key of Object.keys(responseObj)){
            errors.push(responseObj[key]);
        }
        return `(${jqXHR.status}. ${jqXHR.statusText}) ${errors.join(" ")}`
    }
    return "Произошла сетевая ошибка..."
}