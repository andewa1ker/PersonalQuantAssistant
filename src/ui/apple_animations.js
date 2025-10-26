/**
 * Apple级别动画库
 * 包含数字计数、Hero标题、滚动效果等高级动画
 */

// ===== 工具函数 =====
const easeOutExpo = (t) => t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
const easeInOutCubic = (t) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;

/**
 * Apple风格数字计数动画 (CountUp.js风格)
 * 从0增长到目标值，带ease-out-expo缓动和scale效果
 * 
 * @param {string} elementId - 目标元素ID
 * @param {number} targetValue - 目标数值
 * @param {number} duration - 动画时长(毫秒), 默认1200ms
 * @param {string} suffix - 后缀(如 '%', 'K'), 默认空
 * @param {number} decimals - 小数位数, 默认0
 */
function countUpAnimation(elementId, targetValue, duration = 1200, suffix = '', decimals = 0) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // 提取纯数字(移除$, %, K, M, B等)
    const numericValue = parseFloat(targetValue.toString().replace(/[^0-9.-]/g, ''));
    if (isNaN(numericValue)) return;
    
    const startTime = performance.now();
    const startValue = 0;
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOutExpo(progress);
        
        const currentValue = startValue + (numericValue - startValue) * easedProgress;
        
        // 格式化数字(处理K, M, B单位)
        let displayValue;
        if (targetValue.toString().includes('K')) {
            displayValue = (currentValue / 1000).toFixed(decimals) + 'K';
        } else if (targetValue.toString().includes('M')) {
            displayValue = (currentValue / 1000000).toFixed(decimals) + 'M';
        } else if (targetValue.toString().includes('B')) {
            displayValue = (currentValue / 1000000000).toFixed(decimals) + 'B';
        } else {
            displayValue = currentValue.toFixed(decimals);
        }
        
        // 添加前缀(如$)
        if (targetValue.toString().startsWith('$')) {
            displayValue = '$' + displayValue;
        }
        
        element.textContent = displayValue + suffix;
        
        // 动画期间微弱放大效果
        const scale = 1 + (Math.sin(progress * Math.PI) * 0.05);
        element.style.transform = `scale(${scale})`;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.transform = 'scale(1)';
        }
    }
    
    requestAnimationFrame(animate);
}

/**
 * Hero标题逐字符显示动画 (Apple.com风格)
 * 每个字符依次淡入+上浮
 * 
 * @param {string} elementId - 目标元素ID
 * @param {number} staggerDelay - 字符间隔时间(毫秒), 默认20ms
 */
function heroTitleAnimation(elementId, staggerDelay = 20) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const text = element.textContent;
    element.innerHTML = '';
    element.style.display = 'inline-block';
    
    // 将文本拆分为字符并包裹span
    const chars = text.split('').map((char, index) => {
        const span = document.createElement('span');
        span.textContent = char === ' ' ? '\u00A0' : char; // 保留空格
        span.style.cssText = `
            display: inline-block;
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
        `;
        element.appendChild(span);
        
        // 延迟显示
        setTimeout(() => {
            span.style.opacity = '1';
            span.style.transform = 'translateY(0)';
        }, index * staggerDelay);
        
        return span;
    });
}

/**
 * 卡片依次上浮动画 (Stagger效果)
 * 
 * @param {string} containerSelector - 容器选择器(如 '.card-container')
 * @param {number} staggerDelay - 卡片间隔时间(毫秒), 默认150ms
 */
function cardsStaggerAnimation(containerSelector, staggerDelay = 150) {
    const cards = document.querySelectorAll(containerSelector);
    if (!cards.length) return;
    
    cards.forEach((card, index) => {
        card.style.cssText = `
            opacity: 0;
            transform: translateY(40px);
            transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
        `;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * staggerDelay);
    });
}

/**
 * Intersection Observer - 滚动到视口时触发动画
 * 用于数字计数的懒加载
 * 
 * @param {string} selector - 目标元素选择器
 * @param {function} callback - 进入视口时的回调函数
 * @param {number} threshold - 可见度阈值(0-1), 默认0.5
 */
function observeOnScroll(selector, callback, threshold = 0.5) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                callback(entry.target);
                observer.unobserve(entry.target); // 只触发一次
            }
        });
    }, { threshold });
    
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => observer.observe(el));
}

/**
 * 进度条增长动画 (Apple风格)
 * 
 * @param {string} elementId - 进度条元素ID
 * @param {number} targetWidth - 目标宽度百分比(0-100)
 * @param {number} duration - 动画时长(毫秒), 默认1000ms
 */
function progressBarAnimation(elementId, targetWidth, duration = 1000) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startTime = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeInOutCubic(progress);
        
        const currentWidth = targetWidth * easedProgress;
        element.style.width = currentWidth + '%';
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

/**
 * 页面加载完成后自动初始化所有动画
 */
function initAppleAnimations() {
    // 自动为所有带 data-target 属性的元素添加计数动画
    document.querySelectorAll('[data-target]').forEach(el => {
        const target = el.getAttribute('data-target');
        const suffix = el.getAttribute('data-suffix') || '';
        const decimals = parseInt(el.getAttribute('data-decimals') || '0');
        
        observeOnScroll(`#${el.id}`, () => {
            countUpAnimation(el.id, target, 1200, suffix, decimals);
        }, 0.3);
    });
    
    // 自动为带 hero-title 类的元素添加标题动画
    document.querySelectorAll('.hero-title').forEach(el => {
        heroTitleAnimation(el.id);
    });
    
    // 自动为带 stagger-cards 类的容器添加卡片动画
    document.querySelectorAll('.stagger-cards').forEach(container => {
        observeOnScroll('.stagger-cards', () => {
            cardsStaggerAnimation('.modern-card', 150);
        }, 0.1);
    });
}

// DOM加载完成后自动初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAppleAnimations);
} else {
    initAppleAnimations();
}

// 导出函数供外部调用
if (typeof window !== 'undefined') {
    window.AppleAnimations = {
        countUpAnimation,
        heroTitleAnimation,
        cardsStaggerAnimation,
        observeOnScroll,
        progressBarAnimation,
        initAppleAnimations
    };
}
