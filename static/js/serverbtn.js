function flush_table() {
    $.get('/nginx-server',
        function(data){
            var head = document.createElement('div');
            head.setAttribute('class','table-tr');
            head.innerHTML = '<div class="table-th th1" style="text-align: center;">Config</div>\n' +
                            '<div class="table-th th2">Status</div>\n' +
                            '<div class="table-th th3" style="text-align: center;">Actions</div>\n';

            if (data.sites.length > 0){
                // id="tbl-svr"
                table_clear();
                var tbody = document.getElementById('tbl-svr');
                tbody.appendChild(head);
                for(var i = 0;i < data.sites.length; i++){ //遍历一下json数据  
                    var trow = getDataRow(data.sites[i]); //定义一个方法,返回tr数据  
                    tbody.appendChild(trow);  
                }
                table_click();
            }
            else {
                table_clear();
                $('#tbl-svr').append('<div align="center">You don\'t have any site configured.</div>');
            }
        });
    }

function getDataRow(h){  
    var row = document.createElement('div'); //创建行  
    row.setAttribute('filename', h.file);
    row.setAttribute('class','table-tr');

    var nameCell = document.createElement('div');//1
    nameCell.innerHTML = '<btn class="btn btn-link btn-default name-edit" data-toggle="modal" data-target="#rename_server_Modal">'+ h.file +'</btn>';
    nameCell.setAttribute('class','table-td td1');
    row.appendChild(nameCell);

    var statusCell = document.createElement('div');//2
    statusCell.setAttribute('class','table-td td2');
      if (h.choose == "on"){
          statusCell.innerHTML = '<div class="light on"/>';
      }else {
          statusCell.innerHTML = '<div class="light off"/>';
      }
    row.appendChild(statusCell);  

    var ops = document.createElement('div');//3
    ops.setAttribute('class','table-td td3');
    ops.innerHTML = '<btn class="btn btn-link btn-default srv-edit" >编辑</btn>' +
                    '<btn class="btn btn-link btn-default srv-delete">删除</btn>' +
                    '<btn class="btn btn-link btn-default srv-enable">开启</btn>' +
                    '<btn class="btn btn-link btn-default srv-disable">关闭</btn>';
    row.appendChild(ops);

    return row; //返回tr数据      
     }

function table_clear() {
    document.getElementById('tbl-svr').innerHTML= "" ;
}

function name_split(fileName) {
    var first = fileName.lastIndexOf(".");//取到文件名开始到最后一个点的长度
    var namelength = fileName.length;//取到文件名长度
    var filesuffix = fileName.substring(first + 1, namelength );//截取获得后缀名
    var fname = fileName.substring(0, first); //截取文件名，不含后缀
    return [fname, filesuffix]
}

function table_click() {
    $(".name-edit").click(function (event) {
        //event.preventDefault();
        var thisname = $(this).parent().parent().attr('filename');
        var names = name_split(thisname);
        //console.log(names);
        $('#rename_input').val(names[0]);
        $('#src_name').val(thisname);
        $('#suff').val(names[1]);
    });

    $("#svr_rename").click(function () {
        var name =  $('#rename_input').val();
        var src_name = $('#src_name').val();
        var suff = $('#suff').val();
        if (name != src_name && name!=null && name!="" ){
            var new_fullname = name + "." + suff;
            var data = { 'src_name': src_name, 'new_name': new_fullname };
            $.post("/rename-site", data, function (msg) {
                $('#rename_server_Modal').modal('hide');
                tmsg(msg.title, msg.msg, msg.type);
                flush_table();
            });
        }
    })

    $(".srv-edit").click(function (event) {
        event.preventDefault();
        var data = {'name': $(this).parent().parent().attr('filename') };
        $(".lg-container").load("/edit-site", data);
    });

    $(".srv-delete").click(function (event) {
        event.preventDefault();
        var data = {'name': $(this).parent().parent().attr('filename') };
        $.get("/delete-site", data, function (msg) {
            tmsg(msg.title, msg.msg, msg.type);
            flush_table();
        });
    });

    $(".srv-enable").click(function (event) {
        event.preventDefault();
        var data = {'name': $(this).parent().parent().attr('filename') };
        $.get("/enable-site", data, function (msg) {
            tmsg(msg.title, msg.msg, msg.type);
            flush_table();
        });
    });

    $(".srv-disable").click(function (event) {
        event.preventDefault();
        var data = {'name': $(this).parent().parent().attr('filename') };
        $.get("/disable-site", data, function (msg) {
            tmsg(msg.title, msg.msg, msg.type);
            flush_table();
        });
    });
}