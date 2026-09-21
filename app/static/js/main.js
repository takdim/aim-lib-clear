document.addEventListener('DOMContentLoaded', function() {
    // Render UTC timestamps into the user's device timezone.
    function localizeDateTimes() {
        const locale = navigator.language || 'id-ID';
        const nodes = document.querySelectorAll('[data-local-datetime][data-utc]');

        const formatOptions = {
            datetime: {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            },
            'datetime-long': {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            },
            'date-short': {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
            },
            'date-long': {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
            },
            time: {
                hour: '2-digit',
                minute: '2-digit',
            },
        };

        nodes.forEach(node => {
            const utcValue = node.getAttribute('data-utc');
            if (!utcValue) return;

            const date = new Date(utcValue);
            if (Number.isNaN(date.getTime())) return;

            const formatKey = node.getAttribute('data-local-format') || 'datetime';
            const options = formatOptions[formatKey] || formatOptions.datetime;

            node.textContent = date.toLocaleString(locale, options);
            node.setAttribute('title', date.toLocaleString(locale, {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZoneName: 'short',
            }));
        });
    }

    localizeDateTimes();

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

    const noKtmCheckbox = document.getElementById('tidak_punya_ktm');
    const ktmInput = document.getElementById('file_kartu_mahasiswa');
    const ktmTemplateNote = document.getElementById('ktmTemplateNote');

    function syncKtmInputState() {
        if (!ktmInput) return;
        const disabled = !!noKtmCheckbox && noKtmCheckbox.checked;
        ktmInput.disabled = disabled;
        ktmInput.required = !disabled;
        if (ktmTemplateNote) {
            ktmTemplateNote.style.display = disabled ? 'block' : 'block';
        }
    }

    if (noKtmCheckbox && ktmInput) {
        noKtmCheckbox.addEventListener('change', syncKtmInputState);
        syncKtmInputState();
    }

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
