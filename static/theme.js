// Modern UI Interactions
document.addEventListener('DOMContentLoaded', function() {

    // Add smooth scroll behavior for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add entrance animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card-modern, .tech-card, .team-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add floating animation variance to cards
    document.querySelectorAll('.floating-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 2}s`;
        card.style.animationDuration = '6s';
    });

    // Add hover sound effect simulation (visual feedback)
    document.querySelectorAll('.btn-modern, .feature-card-modern, .team-card').forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.filter = 'brightness(1.1)';
        });
        
        el.addEventListener('mouseleave', function() {
            this.style.filter = '';
        });
    });
});