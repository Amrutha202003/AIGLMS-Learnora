function scrollToSection(sectionClass) {
    const section = document.querySelector("." + sectionClass + "-section");
    section.scrollIntoView({ behavior: "smooth" });
}

const swiper = new Swiper('.slider-wrapper', {
  loop: true,
  spaceBetween: 25,

  // If we need pagination
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
    dynamicBullets: true,
  },

  // Navigation arrows
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },

  breakpoints: {
    0:{
        slidesPerView: 1
    },
    768:{
        slidesPerView: 2
    },
    1024:{
        slidesPerView: 3
    },
  }

});



// Show degree field
document.getElementById("grade").addEventListener("change", function() {
    const degreeField = document.getElementById("degreeField");
    if(this.value === "UG" || this.value === "PG"){
        degreeField.classList.remove("hidden");
    } else {
        degreeField.classList.add("hidden");
    }
});

// Contact method switch
document.querySelectorAll("input[name='contact']").forEach(radio => {
    radio.addEventListener("change", function(){
        if(this.value === "phone"){
            document.getElementById("phoneField").classList.remove("hidden");
            document.getElementById("emailField").classList.add("hidden");
        } else {
            document.getElementById("phoneField").classList.add("hidden");
            document.getElementById("emailField").classList.remove("hidden");
        }
    });
});

// Indian Phone Validation
document.getElementById("phoneInput").addEventListener("input", function(){
    this.value = this.value.replace(/[^0-9]/g,"");
    if(this.value.length > 10){
        this.value = this.value.slice(0,10);
    }
});

// OTP simulation
document.getElementById("verifyBtn").addEventListener("click", function(){
    document.getElementById("otpSection").classList.remove("hidden");
});