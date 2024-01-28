function sendArticleComment(articleId) {
    var comment = $('#commentText').val();
    var parentId = $('#parent_id').val();
    console.log(parentId);
    $.get('/articles/add-article-comment', {
        article_comment: comment,
        article_id: articleId,
        parent_id: parentId
    }).then(res => {
        $('#comments_area').html(res);
        $('#commentText').val('');
        $('#parent_id').val('');

        if (parentId !== null && parentId !== '') {
            document.getElementById('single_comment_box_' + parentId).scrollIntoView({behavior: "smooth"});
        } else {
            document.getElementById('comments_area').scrollIntoView({behavior: "smooth"});
        }
    });
}

function fillParentId(parentId) {
    $('#parent_id').val(parentId);
    document.getElementById('comment_form').scrollIntoView({behavior: "smooth"});
}

/*function filterStations() {
    const filterCode = $('#sl2').val();
    const start_code = filterCode.split(',')[0];
    const end_code = filterCode.split(',')[1];
    $('#start_code').val(start_code);
    $('#end_code').val(end_code);
    $('#filter_form').submit();
}*/

function fillPage(page) {
    $('#page').val(page);
    $('#filter_form').submit();
}

function showLargeImage(imageSrc) {
    $('#main_image').attr('src', imageSrc);
    $('#show_large_image_modal').attr('href', imageSrc);
}

$(document).ready(function () {
    $(document).on("click", ".editable", function () {
        var value = $(this).text();
        var input = "<input type='number' min='0' value='" + value + "' class='form-control text-center'>";
        $(this).html(input);
        $(this).removeClass("editable");
    })
    $(document).on("blur", ".form-control", function () {
        var value = $(this).val();
        var td = $(this).parent(td);

        // بررسی اعتبار داده
        if (isNaN(value) || value < 0) {
            alert("فقط اعداد مثبت مجاز هستند.");
            $(this).val("");
            $(this).focus();
            return;
        }

        $(this).remove();
        td.html(value);
        td.addClass("editable text-center");
        var type = td.data("type");
        sendToServer(td.data("id"), value, type);
    })
    $(document).on("keypress", "input-data", function (e) {
        var key = e.which;
        if (key == 13) {
            var value = $(this).val();
            var td = $(this).parent(td);

            // بررسی اعتبار داده
            if (isNaN(value) || value < 0) {
                alert("فقط اعداد مثبت مجاز هستند.");
                $(this).val("");
                $(this).focus();
                return;
            }

            $(this).remove();
            td.html(value);
            td.addClass("editable");
            var type = td.data("type");
            sendToServer(td.data("id"), value, type);
        }
    });

    function sendToServer(id, value, type) {
        console.log(id);
        console.log(value);
        console.log(type);
        $.ajax({
            url: "http://127.0.0.1:8000/stations/save-rain-gauge-value/",
            type: "POST",
            data: {id: id, type: type, value: value},
        })
            .done(function (response) {
                console.log(response);
            })
            .fail(function () {
                console.log("error");
            });
    }
})
;

function printTable() {
    window.print();
}

