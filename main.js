/* ============================================
   لمسة — JavaScript الأسطوري
   ============================================ */

// ===== Cart State =====
let cart = JSON.parse(sessionStorage.getItem('lamsa-cart') || '[]');

function saveCart() {
    sessionStorage.setItem('lamsa-cart', JSON.stringify(cart));
    updateCartUI();
}

function updateCartUI() {
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    
    document.querySelectorAll('#cartCount').forEach(el => {
        el.textContent = count;
        el.style.display = count > 0 ? 'flex' : 'flex';
    });
    
    const cartItemsEl = document.getElementById('cartItems');
    const cartFooter = document.getElementById('cartFooter');
    const cartTotal = document.getElementById('cartTotal');
    
    if (!cartItemsEl) return;
    
    if (cart.length === 0) {
        cartItemsEl.innerHTML = `
            <div class="cart-empty">
                <span>🍰</span>
                <p>سلتك فارغة</p>
                <small>أضف بعض الحلويات الشهية!</small>
            </div>`;
        if (cartFooter) cartFooter.style.display = 'none';
    } else {
        cartItemsEl.innerHTML = cart.map((item, i) => `
            <div class="cart-item">
                <img src="${item.img}" alt="${item.name}">
                <div class="ci-info">
                    <div class="ci-name">${item.name}</div>
                    <div class="ci-price">${item.qty} × ${item.price} ريال</div>
                </div>
                <button class="ci-remove" onclick="removeFromCart(${i})">✕</button>
            </div>
        `).join('');
        if (cartFooter) {
            cartFooter.style.display = 'block';
            if (cartTotal) cartTotal.textContent = total.toFixed(2) + ' ريال';
        }
    }
}

function addToCart(id, name, price, img) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.qty++;
    } else {
        cart.push({ id, name, price, img, qty: 1 });
    }
    saveCart();
    showToast(`تمت إضافة "${name}" للسلة! 🛒`);
    
    // Animate cart button
    const btn = document.querySelector('.cart-btn');
    if (btn) {
        btn.style.transform = 'scale(1.2)';
        setTimeout(() => btn.style.transform = '', 200);
    }
}

function removeFromCart(index) {
    cart.splice(index, 1);
    saveCart();
}

function toggleCart() {
    const sidebar = document.getElementById('cartSidebar');
    const overlay = document.getElementById('cartOverlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }
}

function checkout() {
    if (cart.length === 0) return;
    showToast('شكراً لطلبك! سيتم التواصل معك قريباً 🎉', 'success');
    cart = [];
    saveCart();
    toggleCart();
}

// ===== Toast Notifications =====
function showToast(message, type = 'info') {
    const existing = document.querySelector('.lamsa-toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = 'lamsa-toast';
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        background: #3d1f0d;
        color: white;
        padding: 14px 24px;
        border-radius: 100px;
        font-family: 'Tajawal', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        z-index: 1000;
        box-shadow: 0 10px 40px rgba(0,0,0,0.25);
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease;
        opacity: 0;
        border-right: 4px solid #e67e22;
        white-space: nowrap;
        max-width: 90vw;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
        toast.style.opacity = '1';
    });
    
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(100px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// ===== Navbar Scroll Effect =====
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 20);
    }
});

// ===== Scroll Animations =====
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

function initAnimations() {
    const elements = document.querySelectorAll('.product-card, .feature-card, .kpi-card, .pm-card, .sec-kpi');
    elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s`;
        observer.observe(el);
    });
}

// ===== Smooth Scroll =====
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ===== Flash message auto-dismiss =====
setTimeout(() => {
    document.querySelectorAll('.flash-msg').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-10px)';
        el.style.transition = 'all 0.3s ease';
        setTimeout(() => el.remove(), 300);
    });
}, 4000);

// ===== Product Card Product Modal Placeholder =====
function openProductModal(id) {
    window.location.href = `/product/${id}`;
}

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();
    initAnimations();
    
    // Stagger hero elements
    const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-actions, .hero-stats');
    heroElements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = `opacity 0.6s ease ${i * 0.1 + 0.1}s, transform 0.6s ease ${i * 0.1 + 0.1}s`;
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 50);
    });
    
    const heroVisual = document.querySelector('.hero-visual');
    if (heroVisual) {
        heroVisual.style.opacity = '0';
        heroVisual.style.transform = 'translateX(-30px)';
        heroVisual.style.transition = 'opacity 0.8s ease 0.4s, transform 0.8s ease 0.4s';
        setTimeout(() => {
            heroVisual.style.opacity = '1';
            heroVisual.style.transform = 'translateX(0)';
        }, 50);
    }
});