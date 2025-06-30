// Force VoltFix brand name to be white in admin sidebar
document.addEventListener('DOMContentLoaded', function() {
    // Function to apply white color to brand elements
    function applyWhiteColor() {
        const brandSelectors = [
            '.sidebar .brand-link',
            '.sidebar .brand-text',
            '.sidebar .sidebar-brand',
            '.sidebar .sidebar-brand-text',
            '.sidebar .nav-sidebar .nav-header',
            '.sidebar .nav-sidebar .nav-header a',
            '.sidebar .nav-sidebar .nav-header span',
            '.sidebar .nav-sidebar .nav-header div'
        ];
        
        brandSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.style.color = 'white';
                element.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.3)';
                element.style.fontWeight = '700';
                element.style.fontSize = '1.25rem';
            });
        });
        
        // Also apply to any text content containing "VoltFix"
        const allElements = document.querySelectorAll('.sidebar *');
        allElements.forEach(element => {
            if (element.textContent && element.textContent.includes('VoltFix')) {
                element.style.color = 'white';
                element.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.3)';
                element.style.fontWeight = '700';
            }
        });
    }
    
    // Apply immediately
    applyWhiteColor();
    
    // Apply again after a short delay to catch any dynamically loaded content
    setTimeout(applyWhiteColor, 100);
    setTimeout(applyWhiteColor, 500);
    setTimeout(applyWhiteColor, 1000);
    
    // Watch for DOM changes and reapply
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                applyWhiteColor();
            }
        });
    });
    
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        observer.observe(sidebar, { childList: true, subtree: true });
    }
}); 