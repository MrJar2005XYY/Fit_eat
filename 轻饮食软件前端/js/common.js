/**
 * 轻饮食 - 公共JavaScript
 *
 * 包含导航、工具函数、公共交互等
 */

// 当前页面路径配置
const PAGES = {
  home: 'pages/home.html',
  discover: 'pages/discover.html',
  record: 'pages/record.html',
  community: 'pages/community.html',
  profile: 'pages/profile.html',
  foodDetail: 'pages/food-detail.html',
  aiSetup: 'pages/ai-setup.html',
  aiPlan: 'pages/ai-plan.html',
  myPosts: 'pages/my-posts.html'
};

// 页面标题配置
const PAGE_TITLES = {
  home: '首页',
  discover: '发现',
  record: '记录',
  community: '社区',
  profile: '我的'
};

/**
 * 导航管理器
 */
const Navigation = {
  /**
   * 获取当前活跃的Tab
   */
  getActiveTab() {
    const path = window.location.pathname;
    if (path.includes('home') || path === '/' || path.includes('index')) return 'home';
    if (path.includes('community')) return 'community';
    if (path.includes('discover')) return 'discover';
    if (path.includes('record')) return 'record';
    if (path.includes('profile')) return 'profile';
    return 'home';
  },

  /**
   * 跳转到指定页面
   * @param {string} page - 页面名称
   * @param {Object} params - URL参数
   */
  goto(page, params = {}) {
    const basePath = this.getBasePath();
    let url = basePath + PAGES[page];

    // 添加URL参数
    const queryString = Object.entries(params)
      .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
      .join('&');

    if (queryString) {
      url += '?' + queryString;
    }

    window.location.href = url;
  },

  /**
   * 获取基础路径
   */
  getBasePath() {
    const path = window.location.pathname;
    if (path.includes('/pages/')) {
      return '../';
    }
    return '';
  },

  /**
   * 获取URL参数
   * @param {string} name - 参数名
   * @returns {string|null} 参数值
   */
  getParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
  },

  /**
   * 返回上一页
   */
  back() {
    window.history.back();
  }
};

/**
 * 公共组件渲染器
 */
const Components = {
  /**
   * 渲染顶部导航栏
   * @param {Object} options - 配置选项
   */
  renderTopBar(options = {}) {
    const {
      title = '轻食刻',
      showBack = false,
      showSearch = true,
      showNotification = true,
      showAvatar = true,
      transparent = false,
      rightAction = ''
    } = options;

    const activeTab = Navigation.getActiveTab();
    const basePath = Navigation.getBasePath();

    const tabs = [
      { key: 'home', label: '首页' },
      { key: 'discover', label: '发现' },
      { key: 'record', label: '记录' },
      { key: 'community', label: '社区' },
      { key: 'profile', label: '我的' }
    ];

    return `
      <header class="top-app-bar ${transparent ? 'bg-transparent' : ''}">
        <div class="flex justify-between items-center px-4 md:px-6 h-16 w-full max-w-7xl mx-auto">
          <div class="flex items-center gap-3">
            ${showBack ? `
              <button onclick="Navigation.back()" class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
                <span class="material-symbols-outlined">arrow_back</span>
              </button>
            ` : ''}
            ${showAvatar ? `
              <div class="w-10 h-10 rounded-full overflow-hidden border-2 border-green-500">
                <img src="${API_BASE_URL}/avatar.jpg" alt="头像" class="w-full h-full object-cover"
                     onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDQwIDQwIj48cmVjdCB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIGZpbGw9IiNlMmUyZTIiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzZmN2E2YiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkM8L3RleHQ+PC9zdmc+'">
              </div>
            ` : ''}
            <h1 class="font-bold text-xl text-green-700 tracking-tight">${title}</h1>
            <nav class="hidden md:flex items-center gap-1 ml-6">
              ${tabs.map(tab => `
                <a href="${basePath}${PAGES[tab.key]}"
                   class="desktop-nav-link ${activeTab === tab.key ? 'active' : ''}">${tab.label}</a>
              `).join('')}
            </nav>
          </div>
          <div class="flex items-center gap-2">
            ${rightAction}
            ${showSearch ? `
              <button class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
                <span class="material-symbols-outlined text-green-700">search</span>
              </button>
            ` : ''}
            ${showNotification ? `
              <button class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors relative">
                <span class="material-symbols-outlined text-green-700">notifications</span>
                <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
            ` : ''}
          </div>
        </div>
      </header>
    `;
  },

  /**
   * 渲染底部导航栏
   */
  renderBottomNav() {
    const activeTab = Navigation.getActiveTab();
    const basePath = Navigation.getBasePath();

    const tabs = [
      { key: 'home', icon: 'home', label: '首页' },
      { key: 'discover', icon: 'explore', label: '发现' },
      { key: 'record', icon: 'analytics', label: '记录' },
      { key: 'community', icon: 'group', label: '社区' },
      { key: 'profile', icon: 'person', label: '我的' }
    ];

    return `
      <nav class="bottom-nav mobile-only">
        <div class="flex justify-around items-center">
          ${tabs.map(tab => `
            <a href="${basePath}${PAGES[tab.key]}"
               class="flex flex-col items-center justify-center px-3 py-1 rounded-2xl transition-all ${
                 activeTab === tab.key
                   ? 'bg-green-100 text-green-800'
                   : 'text-gray-500 hover:bg-gray-50'
               }">
              <span class="material-symbols-outlined ${activeTab === tab.key ? 'filled' : ''}">${tab.icon}</span>
              <span class="text-[10px] font-medium mt-0.5">${tab.label}</span>
            </a>
          `).join('')}
        </div>
      </nav>
    `;
  },

  /**
   * 渲染桌面端导航栏
   */
  renderDesktopNav() {
    const activeTab = Navigation.getActiveTab();
    const basePath = Navigation.getBasePath();

    const tabs = [
      { key: 'home', label: '首页' },
      { key: 'discover', label: '发现' },
      { key: 'record', label: '记录' },
      { key: 'community', label: '社区' },
      { key: 'profile', label: '我的' }
    ];

    return `
      <nav class="hidden md:flex items-center gap-6">
        ${tabs.map(tab => `
          <a href="${basePath}${PAGES[tab.key]}"
             class="transition-opacity font-medium ${
               activeTab === tab.key
                 ? 'text-green-700 font-bold'
                 : 'text-gray-600 hover:opacity-80'
             }">${tab.label}</a>
        `).join('')}
      </nav>
    `;
  },

  /**
   * 渲染FAB按钮
   * @param {Object} options - 配置选项
   */
  renderFAB(options = {}) {
    const { icon = 'add', onClick = '', color = 'bg-green-600' } = options;

    return `
      <button class="fab ${color} text-white" onclick="${onClick}">
        <span class="material-symbols-outlined text-3xl">${icon}</span>
      </button>
    `;
  },

  /**
   * 渲染Toast提示
   */
  renderToast() {
    return `
      <div id="toast" class="toast">
        <span class="material-symbols-outlined text-green-400 filled">check_circle</span>
        <span id="toast-message">操作成功</span>
      </div>
    `;
  },

  /**
   * 渲染空状态
   * @param {Object} options - 配置选项
   */
  renderEmptyState(options = {}) {
    const { icon = 'inbox', message = '暂无数据', actionText = '', actionUrl = '' } = options;

    return `
      <div class="empty-state">
        <span class="material-symbols-outlined text-6xl text-gray-300 mb-4">${icon}</span>
        <p class="text-gray-500 mb-4">${message}</p>
        ${actionText ? `
          <a href="${actionUrl}" class="btn-primary">${actionText}</a>
        ` : ''}
      </div>
    `;
  },

  /**
   * 渲染加载状态
   */
  renderLoading() {
    return `
      <div class="flex items-center justify-center py-12">
        <div class="loading-spinner"></div>
      </div>
    `;
  }
};

/**
 * 工具函数
 */
const Utils = {
  /**
   * 判断是否为桌面端
   */
  isDesktop() {
    return window.innerWidth >= 768;
  },
  /**
   * 显示Toast提示
   * @param {string} message - 提示信息
   * @param {number} duration - 显示时长(ms)
   */
  showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    if (toast && toastMessage) {
      toastMessage.textContent = message;
      toast.classList.add('show');

      setTimeout(() => {
        toast.classList.remove('show');
      }, duration);
    }
  },

  /**
   * 格式化数字
   * @param {number} num - 数字
   * @returns {string} 格式化后的字符串
   */
  formatNumber(num) {
    num = num || 0;
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  },

  /**
   * 格式化日期
   * @param {string} dateStr - 日期字符串
   * @returns {string} 格式化后的日期
   */
  formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;

    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
    if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
    if (diff < 604800000) return Math.floor(diff / 86400000) + '天前';

    return `${date.getMonth() + 1}月${date.getDate()}日`;
  },

  /**
   * 防抖函数
   * @param {Function} func - 要防抖的函数
   * @param {number} wait - 等待时间
   * @returns {Function} 防抖后的函数
   */
  debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * 节流函数
   * @param {Function} func - 要节流的函数
   * @param {number} limit - 时间限制
   * @returns {Function} 节流后的函数
   */
  throttle(func, limit = 100) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  /**
   * 生成随机ID
   * @returns {string} 随机ID
   */
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  },

  /**
   * 本地存储封装
   */
  storage: {
    get(key) {
      try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
      } catch {
        return null;
      }
    },

    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch {
        return false;
      }
    },

    remove(key) {
      try {
        localStorage.removeItem(key);
        return true;
      } catch {
        return false;
      }
    }
  }
};

/**
 * 页面初始化
 */
function initPage() {
  // 添加页面加载动画
  document.body.classList.add('animate-fade-in');

  // 初始化工具提示
  initTooltips();

  // 初始化滚动效果
  initScrollEffects();
}

/**
 * 初始化工具提示
 */
function initTooltips() {
  // 为带有 data-tooltip 属性的元素添加工具提示
  document.querySelectorAll('[data-tooltip]').forEach(el => {
    el.addEventListener('mouseenter', function(e) {
      const tooltip = document.createElement('div');
      tooltip.className = 'absolute bg-gray-800 text-white text-xs px-2 py-1 rounded z-50';
      tooltip.textContent = this.dataset.tooltip;
      tooltip.style.top = (e.clientY - 30) + 'px';
      tooltip.style.left = e.clientX + 'px';
      tooltip.id = 'tooltip';
      document.body.appendChild(tooltip);
    });

    el.addEventListener('mouseleave', function() {
      const tooltip = document.getElementById('tooltip');
      if (tooltip) tooltip.remove();
    });
  });
}

/**
 * 初始化滚动效果
 */
function initScrollEffects() {
  const header = document.querySelector('.top-app-bar');

  if (header) {
    window.addEventListener('scroll', Utils.throttle(() => {
      if (window.scrollY > 20) {
        header.classList.add('shadow-md');
        header.classList.remove('bg-transparent');
      } else {
        header.classList.remove('shadow-md');
      }
    }, 100));
  }
}

/**
 * 添加饮食记录弹窗
 */
const AddRecordModal = {
  selectedFood: null,
  searchTimer: null,

  MEAL_TYPES: [
    { key: 'breakfast', label: '早餐', icon: 'wb_sunny' },
    { key: 'lunch', label: '午餐', icon: 'restaurant' },
    { key: 'dinner', label: '晚餐', icon: 'dinner_dining' },
    { key: 'snack', label: '加餐', icon: 'cookie' }
  ],

  getDefaultMeal() {
    const h = new Date().getHours();
    if (h >= 6 && h < 10) return 'breakfast';
    if (h >= 10 && h < 14) return 'lunch';
    if (h >= 14 && h < 17) return 'snack';
    if (h >= 17 && h < 22) return 'dinner';
    return 'snack';
  },

  injectHTML() {
    if (document.getElementById('add-record-modal')) return;
    const html = `
      <div id="add-record-overlay" class="modal-overlay" onclick="AddRecordModal.close()"></div>
      <div id="add-record-modal" class="bottom-sheet">
        <div class="sheet-handle"><span></span></div>
        <div class="px-5 pb-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800">添加饮食记录</h3>
            <button onclick="AddRecordModal.close()" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100">
              <span class="material-symbols-outlined text-gray-500">close</span>
            </button>
          </div>

          <div class="mb-4">
            <label class="text-sm font-medium text-gray-600 mb-2 block">餐类</label>
            <div class="flex gap-2" id="meal-chips"></div>
          </div>

          <div class="mb-4">
            <label class="text-sm font-medium text-gray-600 mb-2 block">搜索食物</label>
            <div class="relative">
              <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xl">search</span>
              <input id="food-search-input" type="text" placeholder="输入食物名称搜索..."
                class="w-full pl-10 pr-4 py-3 bg-gray-100 border-2 border-transparent rounded-xl text-sm focus:outline-none focus:border-green-700 focus:bg-white transition-all"
                oninput="AddRecordModal.onSearch(this.value)">
            </div>
            <div id="food-search-results" class="mt-2 max-h-40 overflow-y-auto hidden"></div>
          </div>

          <div class="space-y-3 mb-5">
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">食物名称</label>
              <input id="record-name" type="text" placeholder="例如：牛油果水波蛋" class="form-input">
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">热量 (kcal)</label>
                <input id="record-calories" type="number" placeholder="0" class="form-input">
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">蛋白质 (g)</label>
                <input id="record-protein" type="number" step="0.1" placeholder="0" class="form-input">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">份量</label>
                <input id="record-amount" type="number" step="0.1" value="1.0" class="form-input">
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">备注</label>
                <input id="record-desc" type="text" placeholder="可选" class="form-input">
              </div>
            </div>
          </div>

          <button onclick="AddRecordModal.submit()" class="w-full py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl text-base transition-colors active:scale-[0.98] shadow-lg shadow-green-200">
            确认添加
          </button>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  },

  open() {
    this.injectHTML();
    this.selectedFood = null;

    // 渲染餐类 chips
    const defaultMeal = this.getDefaultMeal();
    const chipsContainer = document.getElementById('meal-chips');
    chipsContainer.innerHTML = this.MEAL_TYPES.map(m =>
      `<button type="button" class="meal-chip ${m.key === defaultMeal ? 'active' : ''}" data-meal="${m.key}" onclick="AddRecordModal.selectMeal('${m.key}')">
        <span class="material-symbols-outlined text-base">${m.icon}</span>${m.label}
      </button>`
    ).join('');

    // 清空表单
    document.getElementById('food-search-input').value = '';
    document.getElementById('food-search-results').classList.add('hidden');
    document.getElementById('record-name').value = '';
    document.getElementById('record-calories').value = '';
    document.getElementById('record-protein').value = '';
    document.getElementById('record-amount').value = '1.0';
    document.getElementById('record-desc').value = '';

    // 显示弹窗
    document.getElementById('add-record-overlay').classList.add('active');
    document.getElementById('add-record-modal').classList.add('active');

    setTimeout(() => document.getElementById('food-search-input').focus(), 350);
  },

  close() {
    document.getElementById('add-record-overlay').classList.remove('active');
    document.getElementById('add-record-modal').classList.remove('active');
  },

  selectMeal(key) {
    document.querySelectorAll('.meal-chip').forEach(el => {
      el.classList.toggle('active', el.dataset.meal === key);
    });
  },

  getSelectedMeal() {
    const active = document.querySelector('.meal-chip.active');
    return active ? active.dataset.meal : 'breakfast';
  },

  onSearch: Utils.debounce(async function(keyword) {
    const resultsEl = document.getElementById('food-search-results');
    if (!keyword.trim()) {
      resultsEl.classList.add('hidden');
      return;
    }
    try {
      const foods = await API.food.search(keyword);
      if (!foods || foods.length === 0) {
        resultsEl.innerHTML = '<p class="text-sm text-gray-400 px-2 py-2">未找到相关食物</p>';
        resultsEl.classList.remove('hidden');
        return;
      }
      resultsEl.innerHTML = foods.map(f =>
        `<div class="search-result-item" onclick="AddRecordModal.selectFood(${JSON.stringify(f).replace(/"/g, '&quot;')})">
          <div class="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-green-600">restaurant</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-800 truncate">${f.name}</p>
            <p class="text-xs text-gray-500">${f.calories} kcal · 蛋白质 ${f.protein}g</p>
          </div>
        </div>`
      ).join('');
      resultsEl.classList.remove('hidden');
    } catch (e) {
      resultsEl.classList.add('hidden');
    }
  }, 300),

  selectFood(food) {
    this.selectedFood = food;
    document.getElementById('record-name').value = food.name;
    document.getElementById('record-calories').value = food.calories;
    document.getElementById('record-protein').value = food.protein;
    document.getElementById('food-search-input').value = food.name;
    document.getElementById('food-search-results').classList.add('hidden');
  },

  async submit() {
    const name = document.getElementById('record-name').value.trim();
    const calories = parseInt(document.getElementById('record-calories').value) || 0;
    const protein = parseFloat(document.getElementById('record-protein').value) || 0;
    const amount = parseFloat(document.getElementById('record-amount').value) || 1.0;
    const desc = document.getElementById('record-desc').value.trim();
    const meal = this.getSelectedMeal();

    if (!name) {
      Utils.showToast('请输入食物名称');
      return;
    }
    if (calories <= 0) {
      Utils.showToast('请输入热量');
      return;
    }

    try {
      const res = await API.diet.addRecord({
        foodId: this.selectedFood ? this.selectedFood.id : null,
        name,
        meal,
        calories,
        protein,
        amount,
        description: desc
      });

      if (res.success) {
        this.close();
        Utils.showToast('添加成功！');
        // 刷新页面数据
        if (typeof loadPageData === 'function') loadPageData();
        else if (typeof initPage === 'function') initPage();
      } else {
        Utils.showToast(res.message || '添加失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  }
};

/**
 * 编辑账号资料弹窗
 */
const EditProfileModal = {
  userData: null,

  injectHTML() {
    if (document.getElementById('edit-profile-modal')) return;
    const html = `
      <div id="edit-profile-overlay" class="modal-overlay" onclick="EditProfileModal.close()"></div>
      <div id="edit-profile-modal" class="bottom-sheet">
        <div class="sheet-handle"><span></span></div>
        <div class="px-5 pb-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800">账号资料</h3>
            <button onclick="EditProfileModal.close()" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100">
              <span class="material-symbols-outlined text-gray-500">close</span>
            </button>
          </div>

          <div class="space-y-3 mb-5">
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">姓名</label>
              <input id="edit-username" type="text" class="form-input">
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">个人简介</label>
              <input id="edit-bio" type="text" placeholder="介绍一下自己..." class="form-input">
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">性别</label>
                <select id="edit-gender" class="form-input">
                  <option value="">未设置</option>
                  <option value="男">男</option>
                  <option value="女">女</option>
                </select>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">年龄</label>
                <input id="edit-age" type="number" placeholder="0" class="form-input">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">身高 (cm)</label>
                <input id="edit-height" type="number" step="0.1" placeholder="0" class="form-input">
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">体重 (kg)</label>
                <input id="edit-weight" type="number" step="0.1" placeholder="0" class="form-input">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">体脂率 (%)</label>
                <input id="edit-body-fat" type="number" step="0.1" placeholder="0" class="form-input">
              </div>
              <div>
                <label class="text-sm font-medium text-gray-600 mb-1 block">目标体重 (kg)</label>
                <input id="edit-target-weight" type="number" step="0.1" placeholder="0" class="form-input">
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">每日目标热量 (kcal)</label>
              <input id="edit-target-calories" type="number" placeholder="1800" class="form-input">
            </div>
          </div>

          <button onclick="EditProfileModal.submit()" class="w-full py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl text-base transition-colors active:scale-[0.98] shadow-lg shadow-green-200">
            保存修改
          </button>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  },

  async open() {
    this.injectHTML();

    try {
      const user = await API.user.getProfile();
      this.userData = user;

      document.getElementById('edit-username').value = user.name || '';
      document.getElementById('edit-bio').value = user.bio || '';
      document.getElementById('edit-gender').value = user.gender || '';
      document.getElementById('edit-age').value = user.age || '';
      document.getElementById('edit-height').value = user.height || '';
      document.getElementById('edit-weight').value = user.weight || '';
      document.getElementById('edit-body-fat').value = user.body_fat || '';
      document.getElementById('edit-target-weight').value = user.targetWeight || '';
      document.getElementById('edit-target-calories').value = user.targetCalories || 1800;
    } catch (e) {
      console.error('获取用户信息失败:', e);
    }

    document.getElementById('edit-profile-overlay').classList.add('active');
    document.getElementById('edit-profile-modal').classList.add('active');
  },

  close() {
    document.getElementById('edit-profile-overlay').classList.remove('active');
    document.getElementById('edit-profile-modal').classList.remove('active');
  },

  async submit() {
    const data = {
      username: document.getElementById('edit-username').value.trim(),
      bio: document.getElementById('edit-bio').value.trim(),
      gender: document.getElementById('edit-gender').value,
      age: parseInt(document.getElementById('edit-age').value) || 0,
      height: parseFloat(document.getElementById('edit-height').value) || 0,
      weight: parseFloat(document.getElementById('edit-weight').value) || 0,
      body_fat: parseFloat(document.getElementById('edit-body-fat').value) || 0,
      target_weight: parseFloat(document.getElementById('edit-target-weight').value) || 0,
      target_calories: parseInt(document.getElementById('edit-target-calories').value) || 1800
    };

    if (!data.username) {
      Utils.showToast('姓名不能为空');
      return;
    }

    try {
      const res = await API.user.updateProfile(data);
      if (res.success) {
        this.close();
        Utils.showToast('保存成功！');
        // 使用返回的数据直接更新页面显示
        if (res.data && typeof updateProfileDisplay === 'function') {
          updateProfileDisplay(res.data);
        } else if (typeof initPage === 'function') {
          initPage();
        }
      } else {
        Utils.showToast(res.message || '保存失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  }
};

/**
 * 头像选择弹窗
 */
const AvatarModal = {
  DEFAULT_AVATARS: [
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Max',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Luna',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=Mia'
  ],

  injectHTML() {
    if (document.getElementById('avatar-modal')) return;
    const html = `
      <div id="avatar-overlay" class="modal-overlay" onclick="AvatarModal.close()"></div>
      <div id="avatar-modal" class="bottom-sheet">
        <div class="sheet-handle"><span></span></div>
        <div class="px-5 pb-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800">更换头像</h3>
            <button onclick="AvatarModal.close()" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100">
              <span class="material-symbols-outlined text-gray-500">close</span>
            </button>
          </div>

          <div class="mb-5">
            <label class="text-sm font-medium text-gray-600 mb-3 block">选择默认头像</label>
            <div class="grid grid-cols-3 gap-4" id="avatar-grid">
              ${this.DEFAULT_AVATARS.map((url, i) => `
                <div class="flex justify-center">
                  <button onclick="AvatarModal.selectDefault('${url}')" class="w-20 h-20 rounded-full overflow-hidden border-3 border-transparent hover:border-green-500 transition-all hover:scale-105">
                    <img src="${url}" alt="头像${i+1}" class="w-full h-full object-cover">
                  </button>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="mb-5">
            <label class="text-sm font-medium text-gray-600 mb-3 block">或从本地上传</label>
            <div class="flex items-center justify-center w-full">
              <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-2xl cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
                <div class="flex flex-col items-center justify-center pt-5 pb-6">
                  <span class="material-symbols-outlined text-gray-400 text-4xl mb-2">cloud_upload</span>
                  <p class="text-sm text-gray-500">点击选择图片</p>
                  <p class="text-xs text-gray-400 mt-1">支持 JPG、PNG 格式</p>
                </div>
                <input id="avatar-file-input" type="file" class="hidden" accept="image/*" onchange="AvatarModal.handleFileSelect(event)">
              </label>
            </div>
          </div>

          <div id="avatar-preview" class="hidden mb-4 flex flex-col items-center">
            <div class="w-24 h-24 rounded-full overflow-hidden border-4 border-green-500 mb-3">
              <img id="avatar-preview-img" src="" alt="预览" class="w-full h-full object-cover">
            </div>
            <button onclick="AvatarModal.uploadLocal()" class="py-2 px-6 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl text-sm transition-colors">
              使用此头像
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  },

  open() {
    this.injectHTML();
    document.getElementById('avatar-preview').classList.add('hidden');
    document.getElementById('avatar-file-input').value = '';
    document.getElementById('avatar-overlay').classList.add('active');
    document.getElementById('avatar-modal').classList.add('active');
  },

  close() {
    document.getElementById('avatar-overlay').classList.remove('active');
    document.getElementById('avatar-modal').classList.remove('active');
  },

  async selectDefault(url) {
    try {
      const res = await API.user.updateProfile({ avatar: url });
      if (res.success) {
        this.close();
        Utils.showToast('头像更新成功！');
        // 使用返回的数据更新页面
        if (res.data && typeof updateProfileDisplay === 'function') {
          updateProfileDisplay(res.data);
        } else {
          document.getElementById('profile-avatar').src = url;
        }
      } else {
        Utils.showToast(res.message || '更新失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  },

  handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      Utils.showToast('请选择图片文件');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      Utils.showToast('图片大小不能超过5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      document.getElementById('avatar-preview-img').src = e.target.result;
      document.getElementById('avatar-preview').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  },

  async uploadLocal() {
    const imgSrc = document.getElementById('avatar-preview-img').src;
    if (!imgSrc) return;

    try {
      const res = await API.user.updateProfile({ avatar: imgSrc });
      if (res.success) {
        this.close();
        Utils.showToast('头像更新成功！');
        // 使用返回的数据更新页面
        if (res.data && typeof updateProfileDisplay === 'function') {
          updateProfileDisplay(res.data);
        } else {
          document.getElementById('profile-avatar').src = imgSrc;
        }
      } else {
        Utils.showToast(res.message || '更新失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  }
};

/**
 * 修改账户ID弹窗
 */
const AccountSettingsModal = {
  injectHTML() {
    if (document.getElementById('account-settings-modal')) return;
    const html = `
      <div id="account-settings-overlay" class="modal-overlay" onclick="AccountSettingsModal.close()"></div>
      <div id="account-settings-modal" class="bottom-sheet">
        <div class="sheet-handle"><span></span></div>
        <div class="px-5 pb-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800">修改ID或密码</h3>
            <button onclick="AccountSettingsModal.close()" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100">
              <span class="material-symbols-outlined text-gray-500">close</span>
            </button>
          </div>

          <!-- Tab 切换 -->
          <div class="flex bg-gray-100 rounded-xl p-1 mb-5">
            <button id="tab-account-id" onclick="AccountSettingsModal.switchTab('accountId')" class="flex-1 py-2.5 rounded-lg text-sm font-bold text-green-700 bg-white shadow-sm transition-all">修改账户ID</button>
            <button id="tab-password" onclick="AccountSettingsModal.switchTab('password')" class="flex-1 py-2.5 rounded-lg text-sm font-medium text-gray-500 transition-all">修改密码</button>
          </div>

          <!-- 修改账户ID -->
          <div id="panel-account-id" class="space-y-3">
            <div class="p-3 bg-yellow-50 rounded-xl">
              <p class="text-sm text-yellow-700">
                <span class="material-symbols-outlined text-sm align-middle">info</span>
                修改后需使用新账户ID登录
              </p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">当前账户ID</label>
              <input id="current-account-id" type="text" class="form-input bg-gray-50" readonly>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">新账户ID</label>
              <input id="new-account-id" type="text" placeholder="至少3个字符" minlength="3" class="form-input">
            </div>
            <button onclick="AccountSettingsModal.submitAccountId()" class="w-full py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl text-base transition-colors active:scale-[0.98] shadow-lg shadow-green-200">
              确认修改
            </button>
          </div>

          <!-- 修改密码 -->
          <div id="panel-password" class="space-y-3 hidden">
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">旧密码</label>
              <div class="relative">
                <input id="old-password" type="password" placeholder="请输入旧密码" class="form-input pr-10">
                <button type="button" onclick="AccountSettingsModal.togglePassword('old-password', this)" class="absolute right-3 top-1/2 -translate-y-1/2">
                  <span class="material-symbols-outlined text-gray-400 text-xl">visibility_off</span>
                </button>
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">新密码</label>
              <div class="relative">
                <input id="new-password" type="password" placeholder="至少6位" minlength="6" class="form-input pr-10">
                <button type="button" onclick="AccountSettingsModal.togglePassword('new-password', this)" class="absolute right-3 top-1/2 -translate-y-1/2">
                  <span class="material-symbols-outlined text-gray-400 text-xl">visibility_off</span>
                </button>
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-600 mb-1 block">确认新密码</label>
              <div class="relative">
                <input id="confirm-password" type="password" placeholder="再次输入新密码" minlength="6" class="form-input pr-10">
                <button type="button" onclick="AccountSettingsModal.togglePassword('confirm-password', this)" class="absolute right-3 top-1/2 -translate-y-1/2">
                  <span class="material-symbols-outlined text-gray-400 text-xl">visibility_off</span>
                </button>
              </div>
            </div>
            <button onclick="AccountSettingsModal.submitPassword()" class="w-full py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl text-base transition-colors active:scale-[0.98] shadow-lg shadow-green-200">
              确认修改
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  },

  switchTab(tab) {
    const tabId = document.getElementById('tab-account-id');
    const tabPwd = document.getElementById('tab-password');
    const panelId = document.getElementById('panel-account-id');
    const panelPwd = document.getElementById('panel-password');

    if (tab === 'accountId') {
      tabId.className = 'flex-1 py-2.5 rounded-lg text-sm font-bold text-green-700 bg-white shadow-sm transition-all';
      tabPwd.className = 'flex-1 py-2.5 rounded-lg text-sm font-medium text-gray-500 transition-all';
      panelId.classList.remove('hidden');
      panelPwd.classList.add('hidden');
    } else {
      tabId.className = 'flex-1 py-2.5 rounded-lg text-sm font-medium text-gray-500 transition-all';
      tabPwd.className = 'flex-1 py-2.5 rounded-lg text-sm font-bold text-green-700 bg-white shadow-sm transition-all';
      panelId.classList.add('hidden');
      panelPwd.classList.remove('hidden');
    }
  },

  async open() {
    this.injectHTML();

    try {
      const user = await API.user.getProfile();
      document.getElementById('current-account-id').value = user.accountId || '';
    } catch (e) {
      console.error('获取用户信息失败:', e);
    }

    document.getElementById('new-account-id').value = '';
    document.getElementById('old-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-password').value = '';
    this.switchTab('accountId');

    document.getElementById('account-settings-overlay').classList.add('active');
    document.getElementById('account-settings-modal').classList.add('active');
  },

  close() {
    document.getElementById('account-settings-overlay').classList.remove('active');
    document.getElementById('account-settings-modal').classList.remove('active');
  },

  togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('.material-symbols-outlined');
    if (input.type === 'password') {
      input.type = 'text';
      icon.textContent = 'visibility';
    } else {
      input.type = 'password';
      icon.textContent = 'visibility_off';
    }
  },

  async submitAccountId() {
    const newAccountId = document.getElementById('new-account-id').value.trim();

    if (!newAccountId) {
      Utils.showToast('请输入新账户ID');
      return;
    }

    if (newAccountId.length < 3) {
      Utils.showToast('账户ID至少需要3个字符');
      return;
    }

    try {
      const res = await API.user.updateAccountId(newAccountId);
      if (res.success) {
        this.close();
        Utils.showToast('账户ID修改成功！');
        localStorage.setItem('accountId', newAccountId);
        if (res.data && typeof updateProfileDisplay === 'function') {
          updateProfileDisplay(res.data);
        }
      } else {
        Utils.showToast(res.message || '修改失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  },

  async submitPassword() {
    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (!oldPassword || !newPassword || !confirmPassword) {
      Utils.showToast('请填写完整信息');
      return;
    }

    if (newPassword.length < 6) {
      Utils.showToast('新密码至少需要6个字符');
      return;
    }

    if (newPassword !== confirmPassword) {
      Utils.showToast('两次输入的新密码不一致');
      return;
    }

    try {
      const res = await API.user.updatePassword(oldPassword, newPassword);
      if (res.success) {
        this.close();
        Utils.showToast('密码修改成功！');
      } else {
        Utils.showToast(res.message || '修改失败');
      }
    } catch (e) {
      Utils.showToast('网络错误，请重试');
    }
  }
};

// 导出全局对象
window.Navigation = Navigation;
window.Components = Components;
window.Utils = Utils;
window.AddRecordModal = AddRecordModal;
window.EditProfileModal = EditProfileModal;
window.AvatarModal = AvatarModal;
window.AccountSettingsModal = AccountSettingsModal;
window.PAGES = PAGES;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initPage);
