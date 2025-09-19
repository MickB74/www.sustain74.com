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

document.addEventListener('DOMContentLoaded', () => {
    const isNewsPage = document.querySelector('.filter-section');
    if (!isNewsPage) return;

    const categoryFiltersContainer = document.getElementById('categoryFilters');
    const allCards = document.querySelectorAll('.news-card');
    const showAllBtn = document.getElementById('showAllBtn');
    const categoryTags = document.querySelectorAll('.category-tag');

    if (!categoryFiltersContainer || !allCards.length) return;

    const categoryCounts = {};
    allCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (category) {
            categoryCounts[category] = (categoryCounts[category] || 0) + 1;
        }
    });

    const sortedCategories = Object.keys(categoryCounts).sort((a, b) => categoryCounts[b] - categoryCounts[a]);

    sortedCategories.forEach(category => {
        const button = document.createElement('button');
        button.type = 'button'; // Explicitly set button type
        button.className = 'category-filter-btn';
        button.innerHTML = `${category} <span class="category-count">${categoryCounts[category]}</span>`;
        button.dataset.category = category;
        button.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            filterByCategory(category);
            return false;
        };
        categoryFiltersContainer.appendChild(button);
    });

    const filterByCategory = (category) => {
        allCards.forEach(card => {
            if (card.getAttribute('data-category') === category) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });

        document.querySelectorAll('.category-filter-btn').forEach(btn => {
            if (btn.dataset.category === category) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        showAllBtn.style.display = 'inline-block';
        localStorage.setItem('newsCategoryFilter', category);
    };

    const showAllCategories = () => {
        allCards.forEach(card => {
            card.style.display = 'block';
        });
        document.querySelectorAll('.category-filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        showAllBtn.style.display = 'none';
        localStorage.removeItem('newsCategoryFilter');
    };

    categoryFiltersContainer.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        
        const target = event.target.closest('.category-filter-btn');
        if (target) {
            const category = target.dataset.category;
            filterByCategory(category);
        }
    });

    showAllBtn.onclick = (event) => {
        event.preventDefault();
        event.stopPropagation();
        showAllCategories();
        return false;
    };

    categoryTags.forEach(tag => {
        tag.onclick = (event) => {
            event.preventDefault();
            event.stopPropagation();
            const category = tag.textContent;
            filterByCategory(category);
            return false;
        };
    });

    const savedCategory = localStorage.getItem('newsCategoryFilter');
    if (savedCategory) {
        filterByCategory(savedCategory);
    }
});
