$(function () {
    $("#start").click(function () {
        $.ajax({ url: "/start-nginx", success: function(data){
            tmsg(data.title, data.msg, data.type);
            reqs();
            }
        });
    });

    $("#stop").click(function () {
        $.ajax({ url: "/stop-nginx", success: function(data){
            tmsg(data.title, data.msg, data.type);
            reqs();
            }
        });
    });

    $("#reload").click(function () {
        $.ajax({ url: "/reload-nginx", success: function(data){
            //console.log("reload-type: " + data.type)
            tmsg(data.title, data.msg, data.type);
            }
        });
    });

    $("#test").click(function () {
        $.ajax({ url: "/test-nginx", success: function(data){
            tmsg(data.title, data.msg, data.type);
            }
        });
    });
});

$(function () {
    $("#ngxconf_edit").click(function () {
        $(".lg-container").html("");
        $(".lg-container").load("/nginx-config")
    });

    $("#user_edit").click(function () {
        $(".lg-container").html("");
        $(".lg-container").load("/user-config")
    });
});
