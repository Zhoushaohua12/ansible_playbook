// 示例应用 JavaScript 文件
// 用于演示 unarchive 模块的完整应用包解压

document.addEventListener('DOMContentLoaded', function() {
    // 页面加载完成后的初始化
    console.log('示例应用已加载 - 由 Ansible unarchive 模块部署');
    
    // 按钮点击事件
    const heroButton = document.querySelector('#hero button');
    if (heroButton) {
        heroButton.addEventListener('click', function() {
            showNotification('感谢您的关注！这是一个 Ansible 自动化部署的示例应用。');
        });
    }
    
    // 平滑滚动
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (link.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // 动画效果
    animateFeatures();
});

// 显示通知消息
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #667eea;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 特性卡片动画
function animateFeatures() {
    const features = document.querySelectorAll('.feature');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    features.forEach((feature, index) => {
        feature.style.opacity = '0';
        feature.style.transform = 'translateY(20px)';
        feature.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
        observer.observe(feature);
    });
}

// 应用信息
const appInfo = {
    name: '示例应用',
    version: '1.0.0',
    deployedBy: 'Ansible unarchive 模块',
    deployTime: new Date().toISOString(),
    features: [
        '自动化部署',
        '版本管理', 
        '安全校验',
        '完整应用包'
    ]
};

// 导出应用信息（用于调试）
if (typeof window !== 'undefined') {
    window.appInfo = appInfo;
}