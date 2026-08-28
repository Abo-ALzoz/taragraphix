// استخدام مكتبة GSAP لعمل أنيميشن ظهور تدريجي ناعم للعناصر عند فتح الموقع
window.addEventListener("DOMContentLoaded", () => {
    gsap.to("#main-title", { opacity: 1, y: 0, duration: 1, y: -20, ease: "power3.out" });
    gsap.to("#main-desc", { opacity: 1, duration: 1, delay: 0.3, ease: "power3.out" });
    gsap.to("#main-btn", { opacity: 1, duration: 1, delay: 0.6, ease: "power3.out" });
});