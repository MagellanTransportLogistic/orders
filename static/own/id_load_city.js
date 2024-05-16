$('#id_load_city').on('input', function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
        const searchText = $('#id_load_city').val().trim();
        if (searchText.length > 0) {
            $.ajax({
                url: `{% url 'opened_orders:search_city' %}?name=${searchText}`,
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    displayResults(data);
                },
                error: function (error) {
                    console.error(error);
                }
            });
        } else {
            displayResults([]);
        }
    }, 300);
});

function displayResults(results) {
    if (results.length === 0) {
        $('#sr_load_city').hide().empty();
        return;
    }
    const resultList = results.map(item => `<li><a class="dropdown-item gx-5" href="#">${item.name}</a></li>`).join('');
    $('#sr_load_city').html(resultList).show();
}

$('#sr_load_city').on('click', 'li', function () {
    const selectedResult = $(this).text();
    $('#id_load_city').val(selectedResult);
    $('#sr_load_city').hide();
});

$(document).on('click', function (event) {
    if (!$('#sr_load_city').is(event.target) && !$('#id_load_city').is(event.target)) {
        $('#sr_load_city').hide();
    }
});