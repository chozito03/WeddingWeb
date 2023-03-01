$(window).scroll(function() {
    if($(window).scrollTop() + $(window).height() == $(document).height()) {
        $.ajax({
            url: '/about-us/',
            type: 'GET',
            success: function(data) {
                $('#about-us-container').html(data);
            }
        });
    }
});
