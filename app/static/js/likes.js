    $(document).ready(function () {

        $(document).on('click', '.like_btn', function () {

            var post_id = $(this).attr('post_id');
            var action = $(this).attr('action');

            req = $.ajax({
                url: '/like/' + post_id + '/' + action,
                type: 'POST',
                data: {post_id: post_id, action: action}
            });

            req.done(function (data) {
                $('.likes' + post_id).html(data);
            });
        });
    });