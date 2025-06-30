// Hero Slideshow Functionality
document.addEventListener('DOMContentLoaded', function() {
    const heroSlides = document.querySelectorAll('.hero-slide');
    const heroIndicators = document.querySelectorAll('.hero-indicator');
    const heroPrevBtn = document.getElementById('heroPrevBtn');
    const heroNextBtn = document.getElementById('heroNextBtn');
    const heroProgressFill = document.getElementById('heroProgressFill');
    
    let currentSlide = 0;
    let slideInterval;
    const slideDuration = 5000; // 5 seconds per slide
    
    // Initialize slideshow
    function initHeroSlideshow() {
        if (heroSlides.length === 0) return;
        
        // Show first slide
        showSlide(0);
        
        // Start automatic slideshow
        startAutoSlideshow();
        
        // Add event listeners
        if (heroPrevBtn) heroPrevBtn.addEventListener('click', prevSlide);
        if (heroNextBtn) heroNextBtn.addEventListener('click', nextSlide);
        
        // Add indicator click events
        heroIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => showSlide(index));
        });
        
        // Pause on hover
        const heroSlideshow = document.querySelector('.hero-slideshow');
        if (heroSlideshow) {
            heroSlideshow.addEventListener('mouseenter', pauseAutoSlideshow);
            heroSlideshow.addEventListener('mouseleave', startAutoSlideshow);
        }
    }
    
    // Show specific slide
    function showSlide(index) {
        // Remove active class from all slides and indicators
        heroSlides.forEach(slide => slide.classList.remove('active'));
        heroIndicators.forEach(indicator => indicator.classList.remove('active'));
        
        // Add active class to current slide and indicator
        if (heroSlides[index]) heroSlides[index].classList.add('active');
        if (heroIndicators[index]) heroIndicators[index].classList.add('active');
        
        currentSlide = index;
        
        // Reset progress bar
        resetProgressBar();
        
        // Restart auto slideshow
        startAutoSlideshow();
    }
    
    // Next slide
    function nextSlide() {
        const nextIndex = (currentSlide + 1) % heroSlides.length;
        showSlide(nextIndex);
    }
    
    // Previous slide
    function prevSlide() {
        const prevIndex = currentSlide === 0 ? heroSlides.length - 1 : currentSlide - 1;
        showSlide(prevIndex);
    }
    
    // Start automatic slideshow
    function startAutoSlideshow() {
        clearInterval(slideInterval);
        slideInterval = setInterval(() => {
            nextSlide();
        }, slideDuration);
        
        // Start progress bar animation
        startProgressBar();
    }
    
    // Pause automatic slideshow
    function pauseAutoSlideshow() {
        clearInterval(slideInterval);
        pauseProgressBar();
    }
    
    // Progress bar functionality
    function startProgressBar() {
        if (!heroProgressFill) return;
        
        heroProgressFill.style.width = '0%';
        heroProgressFill.style.transition = `width ${slideDuration}ms linear`;
        
        // Use setTimeout to ensure the transition is applied
        setTimeout(() => {
            heroProgressFill.style.width = '100%';
        }, 10);
    }
    
    function pauseProgressBar() {
        if (!heroProgressFill) return;
        heroProgressFill.style.transition = 'none';
    }
    
    function resetProgressBar() {
        if (!heroProgressFill) return;
        heroProgressFill.style.transition = 'none';
        heroProgressFill.style.width = '0%';
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            prevSlide();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
        }
    });
    
    // Touch/swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    const heroSlideshow = document.querySelector('.hero-slideshow');
    if (heroSlideshow) {
        heroSlideshow.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        heroSlideshow.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    }
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next slide
                nextSlide();
            } else {
                // Swipe right - previous slide
                prevSlide();
            }
        }
    }
    
    // Initialize the slideshow
    initHeroSlideshow();
    
    // Add fade-in animation for content
    function animateContent() {
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            heroContent.style.opacity = '0';
            heroContent.style.transform = 'translateY(20px)';
            heroContent.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            
            setTimeout(() => {
                heroContent.style.opacity = '1';
                heroContent.style.transform = 'translateY(0)';
            }, 200);
        }
    }
    
    // Animate content on slide change
    const originalShowSlide = showSlide;
    showSlide = function(index) {
        originalShowSlide(index);
        animateContent();
    };
    
    // Initial content animation
    setTimeout(animateContent, 500);
}); 