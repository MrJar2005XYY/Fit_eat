/**
 * 轻饮食 - API 接口
 *
 * 对接 Flask 后端，所有接口均为真实请求
 */

const API_BASE_URL = 'http://localhost:5000/api';

// 工具函数
async function request(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}${url}`, { ...options, headers, credentials: 'include' });

  // 全局处理 401 未授权响应，清除无效 token 并跳转登录页
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('accountId');
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage !== 'login.html' && currentPage !== 'register.html') {
      window.location.href = 'login.html';
    }
    return { success: false, message: '未登录或登录已过期' };
  }

  return res.json();
}

const API = {
  /**
   * 用户相关接口
   */
  user: {
    getProfile: async () => {
      return request('/user/profile');
    },

    updateProfile: async (data) => {
      return request('/user/profile', { method: 'PUT', body: JSON.stringify(data) });
    },

    updateAccountId: async (accountId) => {
      return request('/user/account-id', { method: 'PUT', body: JSON.stringify({ accountId }) });
    },

    updatePassword: async (oldPassword, newPassword) => {
      return request('/user/password', { method: 'PUT', body: JSON.stringify({ oldPassword, newPassword }) });
    },

    login: async (credentials) => {
      const res = await request('/auth/login', { method: 'POST', body: JSON.stringify(credentials) });
      if (res.success && res.token) {
        localStorage.setItem('token', res.token);
      }
      return res;
    },

    register: async (data) => {
      const res = await request('/auth/register', { method: 'POST', body: JSON.stringify(data) });
      if (res.success && res.token) {
        localStorage.setItem('token', res.token);
      }
      return res;
    }
  },

  /**
   * 饮食记录相关接口
   */
  diet: {
    getTodayCalories: async () => {
      return request('/diet/today-calories');
    },

    getTodayMeals: async () => {
      return request('/diet/today-meals');
    },

    getRecords: async (date) => {
      const params = date ? `?date=${date}` : '';
      return request(`/diet/records${params}`);
    },

    addRecord: async (data) => {
      return request('/diet/records', { method: 'POST', body: JSON.stringify(data) });
    },

    deleteRecord: async (id) => {
      return request(`/diet/records/${id}`, { method: 'DELETE' });
    },

    getMacros: async () => {
      return request('/diet/macros');
    },

    getWaterIntake: async () => {
      return request('/diet/water');
    },

    updateWaterIntake: async (amount) => {
      return request('/diet/water', { method: 'PUT', body: JSON.stringify({ amount }) });
    },

    getWeeklyCalories: async () => {
      return request('/diet/weekly-calories');
    },

    getNutritionRadar: async () => {
      return request('/diet/nutrition-radar');
    }
  },

  /**
   * 食物相关接口
   */
  food: {
    getList: async (page = 1, mealType = '') => {
      const params = new URLSearchParams({ page });
      if (mealType && mealType !== 'all') params.append('meal_type', mealType);
      return request(`/food/list?${params}`);
    },

    getDetail: async (id) => {
      return request(`/food/${id}`);
    },

    search: async (keyword) => {
      return request(`/food/search?q=${encodeURIComponent(keyword)}`);
    },

    toggleFavorite: async (id) => {
      return request(`/food/${id}/favorite`, { method: 'POST' });
    }
  },

  /**
   * AI 方案相关接口
   */
  ai: {
    submitBodyData: async (data) => {
      return request('/ai/body-data', { method: 'POST', body: JSON.stringify(data) });
    },

    getPlan: async () => {
      return request('/ai/plan');
    },

    applyPlan: async () => {
      return request('/ai/apply', { method: 'POST' });
    }
  },

  /**
   * 社区相关接口
   */
  community: {
    getPosts: async (page = 1, category = 'all') => {
      return request(`/community/posts?page=${page}&category=${category}`);
    },

    toggleLike: async (postId) => {
      return request(`/community/posts/${postId}/like`, { method: 'POST' });
    },

    comment: async (postId, content) => {
      return request(`/community/posts/${postId}/comment`, { method: 'POST', body: JSON.stringify({ content }) });
    },

    getComments: async (postId, page = 1) => {
      return request(`/community/posts/${postId}/comments?page=${page}`);
    },

    toggleFollow: async (userId) => {
      return request(`/community/follow/${userId}`, { method: 'POST' });
    },

    createPost: async (data) => {
      return request('/community/posts', { method: 'POST', body: JSON.stringify(data) });
    },

    getMyPosts: async (page = 1) => {
      return request(`/community/my-posts?page=${page}`);
    },

    deletePost: async (postId) => {
      return request(`/community/posts/${postId}`, { method: 'DELETE' });
    }
  },

  /**
   * 文件上传接口
   */
  upload: {
    image: async (file) => {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE_URL}/upload/image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: formData
      });
      return res.json();
    }
  },

  /**
   * 成就相关接口
   */
  achievement: {
    getAll: async () => {
      return request('/achievement/all');
    },

    getUnlocked: async () => {
      return request('/achievement/unlocked');
    }
  }
};

// 导出 API 对象
window.API = API;
