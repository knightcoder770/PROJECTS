// Global utilities for CodeLife

// Update sidebar streak on every page load
document.addEventListener('DOMContentLoaded', () => {
  const streakEl = document.getElementById('streak-count');
  if (streakEl) {
    fetch('/api/stats/today')
      .then(r => r.json())
      .then(d => { streakEl.textContent = d.streak || 0; })
      .catch(() => { streakEl.textContent = '0'; });
  }
});
