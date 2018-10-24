function status_loading(on) {
    if (on) $("#cover").fadeIn(100);
    else $("#cover").fadeOut(100);
}

$.ajaxSetup({
    contentType: 'application/json',
    beforeSend: function (xhr) {
        var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
});
