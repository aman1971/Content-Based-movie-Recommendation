$(function () {
    trend_loading();
});

function trend_loading() {
    var api_key = '1a2d51b966ece85423555707eb93beaf';
    var trend_detail = get_trending(api_key);

    trending_details = {
        trend_id: JSON.stringify(trend_detail.trend_id),
        trend_title: JSON.stringify(trend_detail.trend_title),
        trend_poster: JSON.stringify(trend_detail.trend_poster),
    }

    $.ajax({
        type: 'POST',
        data: trending_details,
        url: '/trend_movie',
        dataType: 'html',
        success: function (response) {
            $('body').html(response);
            $(window).scrollTop(0);
            console.log("working properly");
        },
        error: function () {
            alert('Invalid request');
        },

    });

}

function get_trending(api_key) {
    trend_id = [];
    trend_title = [];
    trend_poster = [];
    $.ajax({
        type: 'GET',
        url: "https://api.themoviedb.org/3/trending/all/day?api_key=" + api_key,
        async: false,
        success: function (trend_mov) {
            console.log("trending", trend_mov);

            for (i = 0; i < 20; i++) {
                trend_id.push(trend_mov.results[i].id);
                trend_title.push(trend_mov.results[i].original_title);
                trend_poster.push('https://www.themoviedb.org/t/p/w600_and_h900_bestv2/' + trend_mov.results[i].poster_path);
            }

        },
        error: function () {
            alert("error at trending movies");
        },
    });
    return { 'trend_id': trend_id, 'trend_title': trend_title, 'trend_poster': trend_poster }
}
