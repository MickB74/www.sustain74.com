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

    // Track selected categories
    let selectedCategories = new Set();

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
        button.type = 'button';
        button.className = 'category-filter-btn';
        button.innerHTML = `${category} <span class="category-count">${categoryCounts[category]}</span>`;
        button.dataset.category = category;
        button.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleCategory(category);
            return false;
        };
        categoryFiltersContainer.appendChild(button);
    });

    const toggleCategory = (category) => {
        if (selectedCategories.has(category)) {
            selectedCategories.delete(category);
        } else {
            selectedCategories.add(category);
        }
        
        updateButtonStates();
        applyFilters();
        saveSelectedCategories();
    };

    const updateButtonStates = () => {
        document.querySelectorAll('.category-filter-btn').forEach(btn => {
            const category = btn.dataset.category;
            if (selectedCategories.has(category)) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Show "Show All" button if any categories are selected
        if (selectedCategories.size > 0) {
            showAllBtn.style.display = 'inline-block';
        } else {
            showAllBtn.style.display = 'none';
        }
    };

    const applyFilters = () => {
        if (selectedCategories.size === 0) {
            // Show all cards if no categories selected
            allCards.forEach(card => {
                card.style.display = 'block';
            });
        } else {
            // Show only cards that match selected categories
            allCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (selectedCategories.has(category)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    };

    const showAllCategories = () => {
        selectedCategories.clear();
        updateButtonStates();
        applyFilters();
        localStorage.removeItem('newsCategoryFilters');
    };

    const saveSelectedCategories = () => {
        if (selectedCategories.size > 0) {
            localStorage.setItem('newsCategoryFilters', JSON.stringify(Array.from(selectedCategories)));
        } else {
            localStorage.removeItem('newsCategoryFilters');
        }
    };

    const loadSelectedCategories = () => {
        const saved = localStorage.getItem('newsCategoryFilters');
        if (saved) {
            try {
                const categories = JSON.parse(saved);
                selectedCategories = new Set(categories);
                updateButtonStates();
                applyFilters();
            } catch (e) {
                console.error('Error loading saved categories:', e);
            }
        }
    };

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
            toggleCategory(category);
            return false;
        };
    });

    // Initialize with saved categories
    loadSelectedCategories();
});
