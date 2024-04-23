var id_review = '';

function deleteReview(review_id) {
    document.getElementById("submit_delete_review").style.display = "block";
    id_review = review_id;
}

function notDeleteReview() {
    document.getElementById("submit_delete_review").style.display = "none";
    id_review = '';
}

function deleteReviewAction(district_id, trip_id) {
    var xml = new XMLHttpRequest();
    xml.open('DELETE', '/districts/' + district_id + '/trips/' + trip_id, true);
    xml.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xml.onload = function(){
        var dataReply = JSON.parse(this.responseText)
        alert(dataReply);
    };
    data = JSON.stringify({
        'id': id_review
    });
    xml.send(data);
    document.getElementById("submit_delete_review").style.display = "none";
}
