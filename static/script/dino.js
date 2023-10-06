const dino = document.getElementById('dino');
const cactus = document.getElementById('cactus');
const score_div = document.getElementById('score');
const record_div = document.getElementById('record');
let record = record_div.innerHTML.slice(8);
let score = 0;
let running = true;
let next1 = false;


function save_record_in_bd() // делает запрос на страницу которая сохраняет рекорд
{
    var request = new XMLHttpRequest();
    var data = new FormData;
    request.open('POST', '/save-record', true)
    data.append('record', record);
    request.send(data);
}


document.addEventListener('keydown', function(event) //  если нажата клавиша
{
    if (event.key){
        next1 = true;
    }
    jump();
});


cactus.addEventListener("animationend", function() // если анимация закончилась
{
    cactus.classList.remove('cactusMove');
    if (running){
        score ++;
        score_div.innerHTML = 'Score: ' + score;
        if (score > record){
            record++;
            record_div.innerHTML = 'Record: ' + record;
            save_record_in_bd(record);
        }
    }
}, false)


function jump() // Прыжок
{
    if (dino.classList != 'jump') {
        dino.classList.add('jump');
    }
    setTimeout(function(){
        dino.classList.remove('jump');
    }, 300)
}


setInterval(function(){  // движение кактуса
    if (running){
        cactus.classList.add('cactusMove')
    }
}, 12)


setInterval(function() // проверка на столкновение
{
    let dino_top = parseInt(window.getComputedStyle(dino).getPropertyValue('top'));
    let cactus_left = parseInt(window.getComputedStyle(cactus).getPropertyValue('left'));

    if (cactus_left < 40 && cactus_left > 0 && dino_top > 300) {
        running = false;
        score = 0;
        score_div.innerHTML = 'Score: ' + score;
        cactus.classList.remove('cactusMove');
        let next = confirm('Game Over Продолжить?');
        running = next;
        if (next){
            cactus.classList.add('cactusMove');
        }
    }
    if (next1){
        cactus.classList.add('cactusMove')
        running = true;
        next1 = false;
    }
}, 3)
