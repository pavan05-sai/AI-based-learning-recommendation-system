// script.js – LearningAI client‑side utilities

document.addEventListener('DOMContentLoaded', () => {
    console.log('LearningAI application loaded.');

    // Auto-dismiss flash messages after 5 seconds if they exist
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => msg.remove());
        }, 5000);
    }
});
