var isLoaded = false;
function reqs() {
    $.ajax({
        type: 'get',
        url: '/nginx-status',
        dataType: 'json',
        beforeSend: function() {
            isLoaded = false;
        },
        success: function(res) {
            //console.log(res.status);
            if (res.status == "running"){
                $("#light").removeClass("off").addClass("on");
            }
            if (res.status == "stop"){
                $("#light").removeClass("on").addClass("off");
            }
            $("#status-plain").html(res.status);
        },
        complete: function() {
            isLoaded = true;
        },
        error: function() {
            console.log('请求失败~');
        }
    });
}

function tmsg(title,msg,type){
    $.Toast(title, msg, type, {
            has_icon:false,
            has_close_btn:true,
            fullscreen:false,
            timeout:6000,
            sticky:false,
            has_progress:true,
            rtl:false,
        });
}

function loaddata() {
    $.ajax({
        type: 'get',
        url: '/nginx-server',
        dataType: 'json',
        success: function(data) {
            console.log('数据加载成功');
        },
        complete: function() {
            console.log('数据加载完毕')
        },
        error: function() {
            console.log('请求失败~');
        }
    });
}

loaddata();

reqs();
setInterval(function() {
    isLoaded && reqs();
}, 3000);
