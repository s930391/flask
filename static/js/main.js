$(function () {
    // 點擊submit
    $("#submit").click(chatWithData);
    console.log("Click");
    $("#message").keypress(function (e) {
        // 當按下enter
        if (e.which == 13) {
            chatWithData();
        }
    });
});

function chatWithData() {
    var message = $("#message").val(); // 使用者輸入的問題
    console.log("問題 : " + message);
    $("#dialog").append("我 : " + message + "\n");
    var data = {
        message: message
    };
    $.post("/call_gemini", data, function (data) {
        $("#dialog").append("AI : " + data + "\n");
        $("#dialog").scrollTop($("#dialog")[0].scrollHeight);
        console.log("回答 : " + data);
    });
    $("#message").val("");
    $("#dialog").scrollTop($("#dialog")[0].scrollHeight);
}