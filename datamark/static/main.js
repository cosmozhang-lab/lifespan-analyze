function status_loading(on) {
    if (on) $("#cover").fadeIn(100);
    else $("#cover").fadeOut(100);
}

function save_login(username, password) {
    window.localStorage["auth"] = username + ":" + password;
}
function clear_login() {
    window.localStorage.removeItem("auth");
}
function get_authstr() {
    return window.localStorage["auth"];
}
function get_authinfo() {
    var authstr = window.localStorage["auth"];
    if (authstr) {
        authstr = authstr.split(":");
        return {
            username: authstr[0],
            password: authstr[1]
        };
    } else {
        return undefined;
    }
}

$(function() {
    $("#button-signout").click(function(event) {
        $.ajax({
            url: '/api/login/logout',
            type: 'POST'
        })
        .done(function() {
            window.location.href = "/login";
        })
        .fail(function() {
        })
        .always(function() {
        });
        
    });
})

$.ajaxSetup({
    contentType: 'application/json',
    beforeSend: function (xhr) {
        var csrftoken = $('input[name="csrfmiddlewaretoken"]').val();
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
        // var authstr = get_authstr();
        // if (authstr) xhr.setRequestHeader("Authorization", authstr);
    }
});

function messagebox(title, content) {
    $("#modal-message-title").text(title);
    $("#modal-message-body").text(content);
    $("#modal-message").modal("show");
}

window.location.query = (function(url) {
    var querystr = /\?[^#]+/.exec(url);
    if (!querystr) return {};
    querystr = querystr[0].slice(1);
    var queryarr = querystr.split("&");
    var querydict = {};
    for (var i = 0; i < queryarr.length; i++) {
        var queryitem = queryarr[i].split("=");
        querydict[queryitem[0]] = queryitem[1];
    }
    return querydict;
})(window.location.href);

window.location.uri = (function(url) {
    return /[^\?#]+/.exec(url)[0];
})(window.location.href);

function make_url(uri, query) {
    query = query || {};
    var url = uri;
    var qks = Object.keys(query);
    if (qks.length > 0) {
        var querystr = "?" + qks.map(function(k) { return k + "=" + query[k]; }).join("&");
        url += querystr;
    }
    return url;
}