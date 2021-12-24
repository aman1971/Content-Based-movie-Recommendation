$(function () {
    $("#autoComplete").autocomplete({
        minLength: 2,
        maxResults: 10,
        source: function (request, response) {
            var results = $.ui.autocomplete.filter(film, request.term);
            response(results.slice(0, this.options.maxResults));
        }
    });


    const enter = document.getElementById('autoComplete');

    const inputhandler = function (e) {
        if (e.target.value == "") {
            $('.movie-button').attr('disabled', true);
        }
        else {
            $('.movie-button').attr('disabled', false);
        }


    }

    enter.addEventListener('input', inputhandler);

    $('#autoComplete').keypress(function (e) {
        if (e.which == 13) {
            $('.movie-button').click();
        }
    });

    $('.movie-button').on('click', function () {
        var api_key = 'API KEY';
        var title = correct_word();
        var corrected_arr = corrected_movie(title);

        if (title == "") {
            $('.result').css('display', 'none');
            $('.fail').css('display', 'block');
        }
        else {
            $('.wave').css('display', 'none');
            $('.trend').css('display', 'none');
            $('.sec').attr('class', 'sec1');
            $('.detail_body').attr('class', 'detail_body1')
            $('.form-group').css('top', '50px');
            $('.head').css('top', '0px');
            $('.loading').css('display', 'block');
            correct_load(api_key, corrected_arr);
        }


    });


});

function correct_word() {
    var input_value = $("#autoComplete").val();
    var correct_text;
    if (input_value == "") {
    } else {
        $.ajax({
            type: 'POST',
            url: "/correct",
            async: false,
            data: { 'nam': input_value },
            success: function (corrected) {
                correct_text = corrected;
            },
        });

    }
    return correct_text;
}

function corrected_movie(value) {
    var result = film;
    var n = result.length;
    correct_movie_arr = [];
    for (var i = 0; i < n; i++) {
        if (correct_movie_arr.length >= 10) {
            break;
        } else {
            if (((result[i].toLowerCase()).indexOf(value.toLowerCase())) > -1) {
                correct_movie_arr.push(result[i]);
            }
        }
    }
    console.log(correct_movie_arr);
    return correct_movie_arr;
}

function recommend_movie(e) {
    var api_key = 'API KEY';
    var title = e.getAttribute('title');
    $('.wave').css('display', 'none');
    $('.trend').css('display', 'none');
    $('.head').css('top', '0px');
    $('.loading').css('display', 'block');
    load_details(api_key, title);
}

function load_details(api_key, title) {

    $.ajax({
        type: 'GET',
        url: 'https://api.themoviedb.org/3/search/movie?api_key=' + api_key + '&query=' + title,
        success: function (movie) {
            if (movie.results.length < 1) {
                $('.result').css('display', 'none');
                $('.fail').css('display', 'block');
            } else {
                $('.fail').css('display', 'none');
                $('.result').css('display', 'block');
                var movie_id = movie.results[0].id;
                var movie_title = movie.results[0].original_title;
                recomend_movie(api_key, movie_id, movie_title);
            }
        },
        error: function () {
            alert('Invalid request');
        },
    });
}

function recomend_movie(api_key, movie_id, movie_title) {
    $.ajax({
        type: 'POST',
        url: "/recomend",
        data: { 'name': movie_title },
        success: function (recs) {
            console.log(recs);
            if (recs == "movie not in our database") {
                $('.result').css('display', 'none');
                $('.fail').css('display', 'block');
                $('.loading').css('display', 'none');
            } else {
                $('.sec').attr('class', 'sec1');
                rec_arr = recs.split('--');
                var movie_arr = []
                for (const movie in rec_arr) {
                    movie_arr.push(rec_arr[movie]);
                }
                get_detail(movie_arr, api_key, movie_id, movie_title);
            }

        },
    });
}

function get_detail(movie_arr, api_key, movie_id, movie_title) {

    $.ajax({
        type: 'GET',
        url: 'https://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + api_key,
        success: function (movie_details) {
            var movie_id1 = movie_details.id;
            var movie_title1 = movie_details.original_title;
            details_loading(movie_details, api_key, movie_id, movie_title, movie_arr);
        }

    })
}


function details_loading(movie_details, api_key, movie_id, movie_title, movie_arr) {
    var imdb_id = movie_details.imdb_id;
    var overview = movie_details.overview;
    var rating = movie_details.vote_average;
    var popularity = movie_details.popularity;
    var vote_count = movie_details.vote_count;
    var genres = movie_details.genres;
    var rel_date = new Date(movie_details.release_date);
    var release = rel_date.toDateString();
    var runtime = movie_details.runtime;
    var status = movie_details.status;
    var poster = 'https://image.tmdb.org/t/p/original' + movie_details.poster_path;
    var genre_list = [];
    for (genre in genres) {
        genre_list.push(genres[genre].name);
    }
    var my_genre = genre_list.join(", ");
    var movie_poster = get_poster(api_key, movie_arr);
    var cast_detail = get_cast_detail(movie_id, api_key);
    var cast_individual = get_cast_individual(cast_detail, api_key);
    var tmdb_id = movie_details.id;
    var trailer_key = load_trailer(tmdb_id, api_key);

    details_object = {
        'movie_title': movie_title,
        'imdb_id': imdb_id,
        'overview': overview,
        'rating': rating,
        'popularity': popularity,
        'vote_count': vote_count,
        'release': release,
        'runtime': runtime,
        'status': status,
        'trailer_key': trailer_key,
        'poster': poster,
        'genre_list': my_genre,
        'rec_movie': JSON.stringify(movie_arr),
        'movie_poster': JSON.stringify(movie_poster),
        'cast_id': JSON.stringify(cast_detail.cast_id),
        'cast_name': JSON.stringify(cast_detail.cast_name),
        'cast_char': JSON.stringify(cast_detail.cast_char),
        'cast_profile': JSON.stringify(cast_detail.cast_profile),
        'cast_dob': JSON.stringify(cast_individual.cast_dob),
        'cast_bio': JSON.stringify(cast_individual.cast_bio),
        'cast_birthplace': JSON.stringify(cast_individual.cast_birthplace),

    }

    $.ajax({
        type: 'POST',
        data: details_object,
        url: "/submit_form",
        dataType: 'html',
        success: function (response) {
            $('.result').html(response);
            $('#autoComplete').val('');
            $('.loading').css('display', 'none');
            $(window).scrollTop(0);
        },
        error: function () {
            alert('Invalid request');
        },
    });
}

function get_poster(api_key, movie_arr) {
    poster_arr = []
    poster_rating = []
    poster_release = []
    for (var i in movie_arr) {
        $.ajax({
            type: 'GET',
            url: 'https://api.themoviedb.org/3/search/movie?api_key=' + api_key + '&query=' + movie_arr[i],
            async: false,
            success: function (mov_det) {
                poster_arr.push('https://image.tmdb.org/t/p/original' + mov_det.results[0].poster_path);
                poster_rating.push(mov_det.results[0].vote_average);
                poster_date = new Date(mov_det.results[0].release_date);
                poster_release.push(poster_date.toDateString());
            }
        });
    }
    return { 'poster_arr': poster_arr, 'poster_rating': poster_rating, 'poster_release': poster_release };
}


function get_cast_detail(movie_id, api_key) {
    cast_id = [];
    cast_name = [];
    cast_char = [];
    cast_profile = [];
    $.ajax({
        type: 'GET',
        url: "https://api.themoviedb.org/3/movie/" + movie_id + "/credits?api_key=" + api_key,
        async: false,
        success: function (movie_cast) {
            if (movie_cast.cast.length >= 10) {
                top_10 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
            } else {
                top_10 = [0, 1, 2, 3, 4];
            }
            for (my_cast in top_10) {
                cast_id.push(movie_cast.cast[my_cast].id);
                cast_name.push(movie_cast.cast[my_cast].name);
                cast_char.push(movie_cast.cast[my_cast].character);
                cast_profile.push("https://image.tmdb.org/t/p/original" + movie_cast.cast[my_cast].profile_path);

            }
        },
        error: function () {
            alert("Invalid Request!");
        },
    });

    return { 'cast_id': cast_id, 'cast_name': cast_name, 'cast_char': cast_char, 'cast_profile': cast_profile };
}


function get_cast_individual(cast_detail, api_key) {
    cast_dob = [];
    cast_bio = [];
    cast_birthplace = [];
    for (cast_id in cast_detail.cast_id) {
        $.ajax({
            type: 'GET',
            url: 'https://api.themoviedb.org/3/person/' + cast_detail.cast_id[cast_id] + '?api_key=' + api_key,
            async: false,
            success: function (cast_description) {
                cast_dob.push((new Date(cast_description.birthday)).toDateString().split(' ').slice(1).join(' '));
                cast_bio.push(cast_description.biography);
                cast_birthplace.push(cast_description.place_of_birth)
            },
        });
    }
    return { 'cast_dob': cast_dob, 'cast_bio': cast_bio, 'cast_birthplace': cast_birthplace }
}


function correct_load(api_key, correct_arr) {
    if (correct_arr.length < 1) {
        $('.result').css('display', 'none');
        $('.fail').css('display', 'block');
    } else {
        $('.fail').css('display', 'none');
        $('.result').css('display', 'block');
        corrected_loading(api_key, correct_arr);
    }
}

function corrected_loading(api_key, correct_arr) {
    var corrected_detail = get_corrected(api_key, correct_arr);

    corrected_details = {
        corrected_id: JSON.stringify(corrected_detail.corrected_id),
        corrected_title: JSON.stringify(corrected_detail.corrected_title),
        corrected_poster: JSON.stringify(corrected_detail.corrected_poster),
        corrected_desc: JSON.stringify(corrected_detail.corrected_desc),
    }

    $.ajax({
        type: 'POST',
        data: corrected_details,
        url: '/correct_movie',
        dataType: 'html',
        success: function (response) {
            $('.result').html(response);
            $('#autoComplete').val('');
            $('.loading').css('display', 'none');
            $(window).scrollTop(0);
        },
        error: function () {
            alert('Invalid request');
        },

    });

}

function get_corrected(api_key, correct_arr) {
    corrected_id = [];
    corrected_title = [];
    corrected_poster = [];
    corrected_desc = [];
    for (var i in correct_arr) {
        $.ajax({
            type: 'GET',
            url: 'https://api.themoviedb.org/3/search/movie?api_key=' + api_key + '&query=' + correct_arr[i],
            async: false,
            success: function (movie_det) {
                try {
                    corrected_id.push(movie_det.results[0].id);
                    corrected_title.push(movie_det.results[0].original_title);
                    corrected_poster.push('https://image.tmdb.org/t/p/original' + movie_det.results[0].poster_path);
                    corrected_desc.push(movie_det.results[0].overview);
                } catch
                {
                    console.log('carry on....');
                }

            },
            error: function () {
                console.log("error at trending movies");
            },
        });
    }

    return { 'corrected_id': corrected_id, 'corrected_title': corrected_title, 'corrected_poster': corrected_poster, 'corrected_desc': corrected_desc }
}

function load_trailer(movie_id, api_key) {
    var trailer_id;
    $.ajax({
        type: 'GET',
        url: "https://api.themoviedb.org/3/movie/" + movie_id + "/videos?api_key=" + api_key,
        async: false,
        success: function (trailer) {
            trailer_id = trailer.results[0].key;
        },
    });
    return trailer_id;
}
<<<<<<< HEAD

=======
>>>>>>> origin
