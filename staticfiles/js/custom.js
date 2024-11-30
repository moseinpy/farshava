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
        editedCells.push({id: $td.data("id"), value: value, type: $td.data("type")});
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
            data: {id: id, type: type, value: value},
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

function makeEditable(id) {
    var row = document.getElementById('row-' + id);
    var inputs = row.getElementsByTagName('input');
    var selects = row.getElementsByTagName('select');
    var editButton = row.querySelector('.edit-btn');
    var saveButton = row.querySelector('.save-btn');

    for (var i = 0; i < inputs.length; i++) {
        inputs[i].readOnly = false;
    }
    for (var j = 0; j < selects.length; j++) {
        selects[j].disabled = false;
    }

    editButton.style.display = 'none';
    saveButton.style.display = 'inline-block';
}

document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.btn-select-date');

    // Check if a period is stored in local storage and highlight the corresponding button
    var selectedPeriod = localStorage.getItem('selectedPeriod');
    if (selectedPeriod) {
        buttons.forEach(function (button) {
            if (button.href.includes(selectedPeriod)) {
                button.classList.add('btn-selected');
            }
        });
    }

    buttons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            // Prevent default behavior
            event.preventDefault();

            // Remove the btn-selected class from all buttons
            buttons.forEach(function (btn) {
                btn.classList.remove('btn-selected');
            });

            // Add the btn-selected class to the clicked button
            button.classList.add('btn-selected');

            // Store the selected period in local storage
            var period = new URL(button.href).searchParams.get('period');
            localStorage.setItem('selectedPeriod', period);

            // Navigate to the href of the clicked button
            window.location.href = button.href;
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript file loaded and DOM fully loaded."); // پیام اشکال‌زدایی

    const rows = document.querySelectorAll(".update-table-rainfall tr");
    console.log("Number of rows found:", rows.length); // تعداد سطرهای پیدا شده

    rows.forEach(function (row, rowIndex) {
        console.log(`Processing row ${rowIndex + 1}`); // اطلاعات سطر

        const inputs = row.querySelectorAll(".input-rainfall");
        console.log(`Number of inputs in row ${rowIndex + 1}:`, inputs.length); // تعداد فیلدها

        inputs.forEach((input, index) => {
            console.log(`Processing input ${index + 1} in row ${rowIndex + 1}`); // اطلاعات فیلد

            if (index > 0) {
                input.disabled = true;
            }

            input.addEventListener("input", function () {
                console.log(`Input value changed: ${input.value}`); // مقدار جدید فیلد

                if (input.value.trim() !== "") {
                    if (index + 1 < inputs.length) {
                        inputs[index + 1].disabled = false;
                    }
                } else {
                    for (let i = index + 1; i < inputs.length; i++) {
                        inputs[i].disabled = true;
                        inputs[i].value = "";
                    }
                }
            });
        });
    });
});

