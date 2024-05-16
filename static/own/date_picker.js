$(function () {
    $('#load_date').datepicker({
        language: 'ru',
        pickTime: false,
        autoclose: true,
        startDate: '0d',
        format: 'dd.mm.yyyy',
        weekStart: 1,
        zIndexOffset: 2048
    });
});
$(function () {
    $('#unload_date').datepicker({
        language: 'ru',
        pickTime: false,
        autoclose: true,
        startDate: '0d',
        format: 'dd.mm.yyyy',
        weekStart: 1,
        zIndexOffset: 2048
    });
});