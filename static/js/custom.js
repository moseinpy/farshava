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

function fillPage(page) {
    $('#page').val(page);
    $('#filter_form').submit();
}

function showLargeImage(imageSrc) {
    $('#main_image').attr('src', imageSrc);
    $('#show_large_image_modal').attr('href', imageSrc);
}

$(document).ready(function () {
    var editedCells = [];

    $(document).on("click", ".editable", function () {
        var $td = $(this);
        var value = $td.text();
        var input = "<input type='number' min='0' value='" + value + "' class='numeric-input text-center'>";
        $td.html(input).removeClass("editable");
        $('.numeric-input').focus();
    });

    $(document).on("blur", ".numeric-input", function () {
        var $input = $(this);
        var value = $input.val();
        var $td = $input.closest("td");

        // بررسی اعتبار داده
        if (isNaN(value) || value < 0) {
            alert("فقط اعداد مثبت مجاز هستند.");
            $input.val("").focus();
            return;
        }

        $td.html(value).addClass("editable text-center");
        editedCells.push({ id: $td.data("id"), value: value, type: $td.data("type") });
    });

    $("button[type='submit']").click(function () {
        $.each(editedCells, function (index, cell) {
            sendToServer(cell.id, cell.value, cell.type);
        });
    });

    function sendToServer(id, value, type) {
        console.log(id, value, type); // برای تست
        $.ajax({
            url: "https://farshava.ir/stations/save-rain-gauge-value/",
            // url: "http://127.0.0.1:8000/stations/save-rain-gauge-value/",

            type: "POST",
            data: { id: id, type: type, value: value },
            success: function (response) {
                console.log(response);
            },
            error: function () {
                console.log("error");
            }
        });
    }
});


function printTable() {
    window.print();
}

