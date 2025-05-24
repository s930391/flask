$(function () {
    // 點擊submit
    $(".submit").click(chatWithData);
    console.log("Click");
    $("#talkwords").keypress(function (e) {
        // 當按下enter
        if (e.which == 13) {
            chatWithData();
        }
    });
});

function chatWithData() {
    var words = document.getElementById("words"); //紀錄    
    var talkwords = document.getElementById("talkwords"); // 使用者輸入的問題
    var word = "";

    if (!talkwords.value.trim()) return;
    console.log("問題 : " + talkwords.value);
    word = "<div class='btalk'><span id='bsay'>你：<br>" + talkwords.value + "</span></div>";
    words.innerHTML += word;

    // 重設動畫狀態
    $(".done").removeClass("finish");
    $(".submit").addClass("loading");

    var data = {
        message: talkwords.value
    };
    $.post("/call_gemini", data, function (data) {
        setTimeout(function() {
            $(".submit").addClass("hide-loading");
            $(".done").addClass("finish");
            }, 300);

        var AIword = "";
        AIword = "<div class='atalk'><span id='asay'>推薦小精靈：<br>" + data + "</span></div>";
        console.log("回答 : " + data);
        words.innerHTML += AIword;        

        setTimeout(function() {
            $(".submit").removeClass("loading");
            $(".submit").removeClass("hide-loading");
            $(".done").removeClass("finish");
            $(".failed").removeClass("finish");
            }, 2000);

        words.scrollTop += 50;
    });
    $("#talkwords").val("");
    words.scrollTop = words.scrollHeight;
}