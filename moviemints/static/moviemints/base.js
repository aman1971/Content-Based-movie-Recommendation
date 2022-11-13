function leftScroll() {
    if(document.getElementById("left").className == "scroll_btn")
    {
        const left = document.querySelector(".trend_card");
        left.scrollBy(200, 0);
    }else{
        const left = document.querySelector(".div_cast_card");
        left.scrollBy(200, 0);
    }
}

function rightScroll() {
    if(document.getElementById("right").className == "scroll_btn")
    {
        const right = document.querySelector(".trend_card");
        right.scrollBy(-200, 0);
    }else{
        const right = document.querySelector(".div_cast_card");
        right.scrollBy(-200, 0);
    }
}

function readMoLe() {
    var dots = document.getElementById("dots");
    var moreText = document.getElementById("more");
    var btnText = document.getElementById("myBtn");
  
    if (dots.style.display === "none") {
      dots.style.display = "inline";
      btnText.innerHTML = "Read more";
      moreText.style.display = "none";
    } else {
      dots.style.display = "none";
      btnText.innerHTML = "Read less";
      moreText.style.display = "inline";
    }
  }

function openClose() {
    var open = document.getElementById("trailer");
    var trailer_bg = document.getElementById("trailer_background");
   
    if (open.style.display === "none") {
        open.style.display = "block";
        trailer_bg.style.display = "block";
    } 
    else {
        open.style.display = "none";
        trailer_bg.style.display = "none";
    }
  }