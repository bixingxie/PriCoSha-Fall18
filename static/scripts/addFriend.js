

$(document).ready(function() {
     $("#btn-add").click(function() {
        $.ajax({
            url: "/addFriend",
            type: "POST",
            data: {
                submit_button: $("#btn-add").val(),
                fg_name:$("#select-group").val(),
                usr:$("#select-usr").val()
            },
            success: function() {

            }
        })
        event.preventDefault();
    })

    $("#btn-cancel").click(function() {
         $.ajax({
                url: "/addFriend",
                type: 'POST',
                data: {
                	submit_button: $("#btn-cancel").val()
                },
                success: function(response) {
                    $("#addFriendPage").html(response);
                }
            })
            event.preventDefault();
    })


});