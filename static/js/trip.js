var current_button = 'excellent';

document.getElementById('badButton').onclick = function() {
    current_button = 'bad';
}

document.getElementById('goodButton').onclick = function() {
    current_button = 'good';
}

document.getElementById('excellentButton').onclick = function() {
    current_button = 'excellent';
}

function submitReview(district_id, trip_id) {

    var xml = new XMLHttpRequest();
    xml.open('POST', '/districts/' + district_id + '/trips/' + trip_id, true);
    xml.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xml.onload = function(){
        var dataReply = JSON.parse(this.responseText)
        alert(dataReply);
    };
    // Получаем текущую дату и время
    const currentDate = new Date();

    // Форматируем дату и время в формат, подходящий для SQLAlchemy DateTime
    const formattedDate = currentDate.toISOString().slice(0, 19).replace('T', ' ');
    dataSend = JSON.stringify({
        'title': document.getElementById("floatingTitle").value,
        'text': document.getElementById("exampleFormControlTextarea1").value,
        'button': current_button,
        'date': formattedDate
    });
    xml.send(dataSend);
    document.getElementById("formContainer").style.display = "none";
    document.getElementById("openReviewButton").style.display = "block";
}