$(document).ready(function () {

    $(document).on('click', '.delete_btn', function () {

        var id = $(this).attr('id');

        $(document).on('click', '.confirm_btn', function () {

        req = $.ajax({
            url: '/delete_comment/' + id,
            type: 'POST',
            data: {id: id},
        })

        req.done(function (data) {
        $('#exampleModal').modal('hide')
        $('body').removeClass('modal-open');
        $('.modal-backdrop').remove();
        $('.comments').html(data);
        });
        });
    });
});