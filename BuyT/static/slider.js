let slides = document.querySelectorAll(".slide");
let dots = document.querySelectorAll(".dot");

let current = 0;

function showSlide(index){

    slides.forEach(slide=>slide.classList.remove("active"));

    dots.forEach(dot=>dot.classList.remove("active-dot"));

    slides[index].classList.add("active");

    dots[index].classList.add("active-dot");
}

document.querySelector(".next").onclick=function(){

    current++;

    if(current>=slides.length){
        current=0;
    }

    showSlide(current);
}

document.querySelector(".prev").onclick=function(){

    current--;

    if(current<0){
        current=slides.length-1;
    }

    showSlide(current);
}

dots.forEach((dot,index)=>{

    dot.onclick=function(){

        current=index;

        showSlide(current);

    }

});

setInterval(function(){

    current++;

    if(current>=slides.length){
        current=0;
    }

    showSlide(current);

},3000);