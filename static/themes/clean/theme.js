(function(){
  const root = document.documentElement;
  const key = 'flatblog:theme';
  function setTheme(t){
    root.setAttribute('data-theme', t);
    localStorage.setItem(key, t);
    const icon = document.getElementById('themeIcon');
    if (icon) icon.className = (t === 'dark') ? 'ri-moon-line' : 'ri-sun-line';
  }
  const saved = localStorage.getItem(key);
  if (saved) setTheme(saved);
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) setTheme('dark');
  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('themeToggle');
    if (btn) btn.addEventListener('click', () => {
      setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
    document.querySelectorAll('.markdown img').forEach(img => { img.loading = 'lazy'; });
  });
})();
