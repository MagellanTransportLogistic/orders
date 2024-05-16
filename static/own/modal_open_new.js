let obj = document.getElementById('new_record');

obj.addEventListener('click', function (e) {
        let _url = obj.dataset.href
        $("#ModalWindow").modal("show");
        $.ajax({
            url: _url,
            type: 'get',
            data: {},
            success: function (data) {
                $("#ModalWindow .modal-content").html(data);
            }
        })
    }
);