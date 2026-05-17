document.addEventListener("DOMContentLoaded", () => {

    // Animate cards one by one
    const cards = document.querySelectorAll(".station-card");

    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(40px)";

        setTimeout(() => {
            card.style.transition = "all 0.6s ease";
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, index * 120);
    });

    // Button hover animation
    const buttons = document.querySelectorAll(".book-now-btn");

    buttons.forEach(button => {

        button.addEventListener("mouseenter", () => {
            button.innerHTML =
                `Booking Slot <i class="fa-solid fa-bolt"></i>`;
        });

        button.addEventListener("mouseleave", () => {
            button.innerHTML =
                `Book Now <i class="fa-solid fa-arrow-right"></i>`;
        });

    });

});