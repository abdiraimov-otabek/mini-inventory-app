function appShell() {
    return {
        modalOpen: false,
        toasts: [],
        toastCounter: 0,
        init() {
            window.AppShell = this;
        },
        openModal() {
            this.modalOpen = true;
        },
        closeModal() {
            this.modalOpen = false;
            const panel = document.getElementById('modal-panel');
            if (panel) {
                panel.innerHTML = '';
            }
        },
        addToast(message, type = 'success', detail = '') {
            const id = ++this.toastCounter;
            this.toasts.push({ id, message, type, detail });
            setTimeout(() => this.dismissToast(id), 3000);
        },
        dismissToast(id) {
            this.toasts = this.toasts.filter((toast) => toast.id !== id);
        },
    };
}

function productForm(initialPreview = '') {
    return {
        preview: initialPreview || null,
        dragging: false,
        submitting: false,
        isValid: false,
        rawPrice: '',
        priceInput: null,
        initialize() {
            this.priceInput = this.$el.querySelector('[x-ref="priceInput"]');
            this.$el.addEventListener('input', () => this.validate());
            if (this.priceInput && this.priceInput.value) {
                this.rawPrice = this.priceInput.value.replace(/[^\d]/g, '');
                this.applyFormattedPrice();
            }
            this.validate();
        },
        handleFileChange(event) {
            this.dragging = false;
            const file = event.target.files[0];
            if (!file) {
                return;
            }
            if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
                window.AppShell?.addToast('Faqat jpeg, png yoki webp rasm yuklang.', 'error');
                event.target.value = '';
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                window.AppShell?.addToast('Rasm hajmi 5MB dan oshmasligi kerak.', 'error');
                event.target.value = '';
                return;
            }
            this.preview = URL.createObjectURL(file);
            this.validate();
        },
        handleDrop(event) {
            this.dragging = false;
            const files = event.dataTransfer.files;
            if (!files || !files.length) {
                return;
            }
            const input = event.currentTarget.querySelector('input[type="file"]');
            input.files = files;
            this.handleFileChange({ target: input });
        },
        validate() {
            this.isValid = this.$el.checkValidity();
        },
        formatPrice(event) {
            const input = event.target;
            let digits = input.value.replace(/[^\d]/g, '');
            this.rawPrice = digits;
            if (digits.length === 0) {
                input.value = '';
                this.validate();
                return;
            }
            const formatted = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            input.value = formatted;
            this.validate();
        },
        applyFormattedPrice() {
            if (!this.priceInput) return;
            const formatted = this.rawPrice.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            this.priceInput.value = formatted;
        },
        handleAfterRequest(event) {
            this.submitting = false;
            if (this.priceInput) {
                this.applyFormattedPrice();
            }
            const xhr = event.detail?.xhr;
            if (event.detail?.successful && xhr && xhr.status === 204) {
                window.AppShell?.closeModal();
            }
        },
    };
}

document.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token to all HTMX requests
    const csrfTokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfTokenInput) {
        event.detail.headers['X-CSRFToken'] = csrfTokenInput.value;
    }

    // For product forms, ensure the raw price is sent
    const form = event.target;
    if (form && form.hasAttribute('x-data') && form.getAttribute('x-data').includes('productForm')) {
        // Access Alpine.js component data directly
        const component = form._x_dataStack[0];
        if (component && component.priceInput && typeof component.rawPrice !== 'undefined') {
            const priceInputName = component.priceInput.name;
            event.detail.parameters[priceInputName] = component.rawPrice || '';
        }
    }
});

document.addEventListener('htmx:beforeRequest', () => {
    document.getElementById('global-indicator')?.classList.remove('hidden');
});

document.addEventListener('htmx:afterRequest', () => {
    document.getElementById('global-indicator')?.classList.add('hidden');
});

document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'modal-panel') {
        window.AppShell?.openModal();
    }
});

document.addEventListener('showToast', (event) => {
    const detail = event.detail || {};
    window.AppShell?.addToast(detail.message || 'Notice', detail.type || 'success', detail.detail || '');
});

document.addEventListener('closeModal', () => {
    window.AppShell?.closeModal();
});

document.addEventListener('stopInfiniteScroll', () => {
    const trigger = document.getElementById('load-more-trigger');
    if (trigger) {
        trigger.remove();
    }
    const triggerCards = document.getElementById('load-more-trigger-cards');
    if (triggerCards) {
        triggerCards.remove();
    }
});

document.addEventListener('htmx:responseError', () => {
    window.AppShell?.addToast('Xatolik yuz berdi. Qayta urinib ko‘ring.', 'error');
});
