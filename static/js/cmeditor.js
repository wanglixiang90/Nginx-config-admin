function cmeditor(textobj) {
    var myCodeMirror = CodeMirror.fromTextArea(textobj,{
            height: 600,
            value: textobj.value,
            theme: "eclipse",
            mode: "text/javascript" , //实现Java代码高亮
            indentWithTabs: true,
            smartIndent: true,  //自动缩进
            lineNumbers:true,  // 显示行号
            matchBrackets : true,  //括号匹配
            lineWiseCopyCut: true
    });
    return myCodeMirror;
}

$(function(){
    var myTextarea = document.getElementById("filetext");
    var myCodeMirror = cmeditor(myTextarea);

    setTimeout(function() {
        myCodeMirror.refresh();
    },1);
});