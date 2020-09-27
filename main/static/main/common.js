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
