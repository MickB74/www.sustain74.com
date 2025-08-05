// js/main.js
document.querySelector('.nav-toggle').addEventListener('click', () => {
  document.querySelector('.nav-list').classList.toggle('nav-open');
});

// Sticky CTA Bar
document.addEventListener('scroll', () => {
    const ctaBar = document.querySelector('.sticky-cta-bar');
    if (window.scrollY > 300) {
        ctaBar.classList.add('visible');
    } else {
        ctaBar.classList.remove('visible');
    }
});
