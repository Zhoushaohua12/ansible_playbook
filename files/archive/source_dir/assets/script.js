// 示例应用 JavaScript 文件
// 用于演示 archive 模块的脚本文件归档

// 应用初始化
class ArchiveDemoApp {
    constructor() {
        this.version = '1.0.0';
        this.createdBy = 'Ansible archive 模块';
        this.init();
    }

    init() {
        console.log('📦 归档演示应用已初始化');
        console.log(`📋 版本: ${this.version}`);
        console.log(`🔧 创建者: ${this.createdBy}`);
        console.log(`⏰ 初始化时间: ${new Date().toISOString()}`);
        
        this.bindEvents();
        this.loadArchiveInfo();
    }

    // 绑定事件
    bindEvents() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupUI();
            this.showWelcomeMessage();
        });

        // 按钮事件
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => this.handleButtonClick(e));
        });
    }

    // 设置用户界面
    setupUI() {
        this.updateArchiveStatus();
        this.setupFileList();
        this.setupProgressBar();
    }

    // 显示欢迎消息
    showWelcomeMessage() {
        const message = `
🎉 欢迎使用归档演示应用！

此应用由 Ansible archive 模块创建和归档，包含以下功能：
• 📁 文件和目录归档
• ⚙️ 多种压缩格式支持
• 🚫 灵活的文件排除机制
• 🔒 安全的归档操作
• 📊 详细的归档信息

开始探索归档功能的强大之处吧！
        `;
        
        this.showNotification(message, 'success', 5000);
    }

    // 加载归档信息
    loadArchiveInfo() {
        const archiveInfo = {
            format: 'tar.gz',
            compression: 'gzip',
            excludePaths: ['temp/', '*.tmp'],
            removeSource: false,
            created: new Date().toISOString(),
            size: this.calculateArchiveSize(),
            fileCount: this.countFiles()
        };

        this.archiveInfo = archiveInfo;
        console.log('📊 归档信息:', archiveInfo);
    }

    // 计算归档大小（模拟）
    calculateArchiveSize() {
        return Math.floor(Math.random() * 1000000) + 500000; // 500KB - 1.5MB
    }

    // 统计文件数量（模拟）
    countFiles() {
        return Math.floor(Math.random() * 50) + 10; // 10-60 个文件
    }

    // 处理按钮点击
    handleButtonClick(event) {
        const button = event.target;
        const action = button.textContent.trim();

        switch (action) {
            case '创建归档':
                this.createArchive();
                break;
            case '查看详情':
                this.showArchiveDetails();
                break;
            case '验证完整性':
                this.verifyArchive();
                break;
            case '下载归档':
                this.downloadArchive();
                break;
            default:
                console.log('未知操作:', action);
        }
    }

    // 创建归档（模拟）
    createArchive() {
        this.showProgress('正在创建归档...', 0);
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                this.showProgress('归档创建完成！', 100);
                this.showNotification('✅ 归档创建成功！', 'success');
                this.updateArchiveStatus();
            } else {
                this.showProgress(`正在创建归档... ${Math.floor(progress)}%`, progress);
            }
        }, 300);
    }

    // 显示归档详情
    showArchiveDetails() {
        const details = `
📦 归档详细信息

格式: ${this.archiveInfo.format}
压缩: ${this.archiveInfo.compression}
大小: ${(this.archiveInfo.size / 1024).toFixed(2)} KB
文件数: ${this.archiveInfo.fileCount}
创建时间: ${this.archiveInfo.created}
排除路径: ${this.archiveInfo.excludePaths.join(', ')}
删除源文件: ${this.archiveInfo.removeSource ? '是' : '否'}

归档内容:
• ✅ index.html - 主页面
• ✅ README.md - 说明文档  
• ✅ config/ - 配置文件目录
• ✅ logs/ - 日志文件目录
• ✅ assets/ - 资源文件目录
• ❌ temp/ - 临时文件目录（已排除）
        `;
        
        this.showNotification(details, 'info', 8000);
    }

    // 验证归档完整性
    verifyArchive() {
        this.showProgress('正在验证归档完整性...', 0);
        
        setTimeout(() => {
            const isValid = Math.random() > 0.1; // 90% 概率验证成功
            
            if (isValid) {
                this.showProgress('✅ 归档完整性验证通过！', 100);
                this.showNotification('✅ 归档完整性验证成功！', 'success');
            } else {
                this.showProgress('❌ 归档完整性验证失败！', 100);
                this.showNotification('❌ 归档完整性验证失败，请重新创建归档。', 'error');
            }
        }, 2000);
    }

    // 下载归档（模拟）
    downloadArchive() {
        const filename = `archive_demo_${Date.now()}.tar.gz`;
        console.log(`📥 开始下载归档: ${filename}`);
        
        this.showNotification(`📥 正在下载 ${filename}...`, 'info');
        
        setTimeout(() => {
            this.showNotification(`✅ ${filename} 下载完成！`, 'success');
        }, 1500);
    }

    // 更新归档状态
    updateArchiveStatus() {
        const statusElements = document.querySelectorAll('.archive-status');
        statusElements.forEach(element => {
            element.textContent = `最后更新: ${new Date().toLocaleString()}`;
        });
    }

    // 设置文件列表
    setupFileList() {
        const files = [
            { name: 'index.html', size: '4.2KB', type: 'HTML' },
            { name: 'README.md', size: '2.1KB', type: 'Markdown' },
            { name: 'config/', size: '1.5KB', type: '目录' },
            { name: 'logs/', size: '3.8KB', type: '目录' },
            { name: 'assets/', size: '8.7KB', type: '目录' },
            { name: 'temp/', size: '1.2KB', type: '目录（已排除）' }
        ];

        const fileList = document.querySelector('.file-list');
        if (fileList) {
            fileList.innerHTML = files.map(file => `
                <tr>
                    <td>${file.name}</td>
                    <td>${file.size}</td>
                    <td><span class="status ${file.type.includes('排除') ? 'status-warning' : 'status-success'}">${file.type}</span></td>
                </tr>
            `).join('');
        }
    }

    // 设置进度条
    setupProgressBar() {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = '0%';
        }
    }

    // 显示进度
    showProgress(message, percentage) {
        const progressText = document.querySelector('.progress-text');
        const progressBar = document.querySelector('.progress-bar');
        
        if (progressText) {
            progressText.textContent = message;
        }
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
    }

    // 显示通知
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-message">${message.replace(/\n/g, '<br>')}</div>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // 添加样式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 500px;
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            border-left: 4px solid ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        `;
        
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // 自动隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
}

// 创建应用实例
const app = new ArchiveDemoApp();

// 导出应用对象（用于调试）
if (typeof window !== 'undefined') {
    window.archiveDemoApp = app;
}

// 页面加载完成后的额外设置
window.addEventListener('load', () => {
    console.log('🚀 归档演示应用加载完成');
    console.log('📖 使用 app 对象访问应用功能');
    console.log('🔧 例如: app.createArchive() 创建归档');
});