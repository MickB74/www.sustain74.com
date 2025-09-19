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

// Fallback: remove "Our Solutions" nav item if present to avoid spacing issues
document.addEventListener('DOMContentLoaded', () => {
  const navList = document.querySelector('.nav-list');
  if (!navList) return;
  const solutionsLink = navList.querySelector('a[href="services.html"]');
  if (solutionsLink && solutionsLink.parentElement && solutionsLink.parentElement.tagName === 'LI') {
    solutionsLink.parentElement.remove();
  }
});
