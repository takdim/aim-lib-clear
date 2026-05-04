document.addEventListener('DOMContentLoaded', function() {
    // 1. Navbar Mobile Toggle
    const toggleBtn = document.getElementById('navbarToggle');
    const navMenu = document.getElementById('navbarMenu');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            toggleBtn.classList.toggle('active');
        });
    }

    // 2. Password Visibility Toggle
    const togglePassBtns = document.querySelectorAll('.toggle-password');
    togglePassBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = '🙈';
            } else {
                input.type = 'password';
                this.textContent = '👁';
            }
        });
    });

    // 3. File Upload Name Preview
    const fileInputs = [
        { input: 'file_bebas_pustaka', display: 'file1Name' },
        { input: 'file_kartu_mahasiswa', display: 'file2Name' }
    ];

    fileInputs.forEach(item => {
        const inputEl = document.getElementById(item.input);
        const displayEl = document.getElementById(item.display);
        
        if (inputEl && displayEl) {
            inputEl.addEventListener('change', function() {
                if (this.files && this.files.length > 0) {
                    displayEl.textContent = '✅ Terpilih: ' + this.files[0].name;
                    displayEl.style.color = 'var(--success)';
                } else {
                    displayEl.textContent = '';
                }
            });
        }
    });

    // 4. Auto-hide Flash Messages
    const flashContainer = document.getElementById('flashContainer');
    if (flashContainer) {
        setTimeout(() => {
            const alerts = flashContainer.querySelectorAll('.alert');
            alerts.forEach(alert => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                alert.style.transition = 'all 0.5s ease';
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);
    }
});
