# 轻食刻 — Bug 检查报告

> 检查日期：2026-06-02
>
> 检查范围：后端 Python 代码 + 前端 HTML/JS 代码

---

## 一、后端 Bug（20 个）

### 🔴 高严重性（5 个）— 会导致运行时崩溃

#### Bug 1: `request.get_json()` 返回 None 未处理

- **涉及文件**：`routes/auth.py`、`routes/user.py`、`routes/diet.py`、`routes/community.py`、`routes/achievement.py`
- **问题**：当请求的 `Content-Type` 不是 `application/json` 或请求体不是合法 JSON 时，`request.get_json()` 返回 `None`，随后对 `None` 调用 `.get()` 会抛出 `AttributeError`
- **修复**：
```python
data = request.get_json()
if not data:
    return jsonify({'success': False, 'message': '请求数据无效'}), 400
```

#### Bug 2: 点赞/评论未校验帖子是否存在

- **文件**：`routes/community.py` 第 64-72 行、第 87 行
- **问题**：`toggle_like` 和 `add_comment` 接口没有先验证帖子是否存在，传入不存在的 `post_id` 会导致外键约束错误
- **修复**：
```python
post = CommunityPost.query.get(post_id)
if not post:
    return jsonify({'success': False, 'message': '动态不存在'}), 404
```

#### Bug 3: 关注未校验目标用户是否存在

- **文件**：`routes/community.py` 第 134-152 行
- **问题**：`toggle_follow` 接口没有验证目标用户是否存在，传入不存在的用户 ID 会导致外键约束错误
- **修复**：
```python
target_user = User.query.get(user_id)
if not target_user:
    return jsonify({'success': False, 'message': '用户不存在'}), 404
```

#### Bug 4: `Food.to_dict()` 中 `json.loads` 无异常保护

- **文件**：`models/food.py` 第 37-38 行
- **问题**：当 `ingredients` 或 `steps` 不是合法 JSON 字符串时，`json.loads()` 会抛出 `JSONDecodeError`
- **修复**：
```python
try:
    ingredients = json.loads(self.ingredients) if self.ingredients else []
except (json.JSONDecodeError, TypeError):
    ingredients = []
```

#### Bug 5: `DietRecord.to_dict()` 中 `recorded_at` 可能为 None

- **文件**：`models/diet.py` 第 39 行
- **问题**：`recorded_at` 字段没有设置 `nullable=False`，如果为 None 时调用 `.strftime()` 会抛出 `AttributeError`
- **修复**：
```python
'time': self.recorded_at.strftime('%Y-%m-%d %H:%M') if self.recorded_at else '',
```

---

### 🟡 中严重性（6 个）— 安全漏洞/功能缺陷

#### Bug 6: Admin 后台完全无认证保护

- **文件**：`admin/views.py` 第 7-8 行
- **问题**：`is_accessible()` 直接返回 `True`，任何人访问 `/admin` 都可以操作后台
- **修复**：
```python
def is_accessible(self):
    return current_user.is_authenticated and current_user.account_id == 'admin'
```

#### Bug 7: 认证 Token 可预测

- **文件**：`routes/auth.py` 第 31 行、第 45 行
- **问题**：Token 格式为 `user_1`、`user_2`，任何人都可以伪造
- **修复**：使用 `itsdangerous` 或 `PyJWT` 生成真正的 JWT Token

#### Bug 8: SECRET_KEY 硬编码后备值

- **文件**：`config.py` 第 7 行
- **问题**：环境变量未设置时使用硬编码字符串，攻击者可伪造 session cookie
- **修复**：生产环境强制要求设置 SECRET_KEY 环境变量

#### Bug 9: Flask-Login 初始化但未使用

- **文件**：`app.py` 第 20-27 行、`routes/auth.py` 第 30-31 行
- **问题**：初始化了 `LoginManager` 但从未调用 `login_user(user)`，导致 `current_user` 和 `@login_required` 不工作
- **修复**：登录时调用 `login_user(user)`，或移除 Flask-Login 依赖

#### Bug 10: 收藏列表返回顺序不一致

- **文件**：`routes/food.py` 第 77-80 行
- **问题**：`favs` 按时间排序，但 `Food.id.in_()` 不保证顺序
- **修复**：
```python
food_map = {f.id: f for f in foods}
foods = [food_map[fid] for fid in food_ids if fid in food_map]
```

#### Bug 11: 用户被删后帖子/评论序列化崩溃

- **文件**：`models/community.py` 第 28-29 行、第 71 行
- **问题**：`self.user` 为 None 时访问 `.username` 会抛出 `AttributeError`
- **修复**：
```python
'name': self.user.username if self.user else '已注销用户',
```

---

### 🟠 中低严重性（5 个）— 性能/逻辑问题

#### Bug 12: `User.to_dict()` 中 N+1 查询

- **文件**：`models/user.py` 第 60-61 行
- **问题**：每次调用 `to_dict()` 都会触发 2 次额外的 SQL COUNT 查询

#### Bug 13: 帖子列表 N+1 查询

- **文件**：`models/community.py` 第 22 行、第 35-36 行
- **问题**：每条帖子序列化时额外执行 3 次 SQL 查询（点赞检查、点赞数、评论数）

#### Bug 14: SQL LIKE 通配符未转义

- **文件**：`import_images.py` 第 101 行
- **问题**：`dish_name` 中的 `%` 或 `_` 会导致意外的模式匹配
- **修复**：使用 `contains()` 或手动转义通配符

#### Bug 15: AI 饮食计划食物推荐回退逻辑脆弱

- **文件**：`routes/achievement.py` 第 187-190 行
- **问题**：当某一餐类型没有食物时，回退逻辑使用硬编码切片，可能返回空列表

#### Bug 16: 初始化数据缺少营养字段

- **文件**：`init_db.py` 第 266-275 行
- **问题**：创建 DietRecord 时只复制了 `calories` 和 `protein`，缺少 `carbs`、`fat`、`fiber`

---

### 🟢 低严重性（4 个）— 边界条件

#### Bug 17: `int(user_id)` 可能 ValueError

- **文件**：`app.py` 第 27 行

#### Bug 18: 日期解析失败静默忽略

- **文件**：`routes/diet.py` 第 74-81 行

#### Bug 19: Favorite 模型未在 `__init__.py` 中导出

- **文件**：`models/__init__.py` 第 8 行

#### Bug 20: `tags` 为 None 时 `.split()` 崩溃

- **文件**：`models/food.py` 第 36 行

---

## 二、前端 Bug（53 个）

### 🔴 高严重性（5 个）

#### Bug 1: `request()` 在非 JSON 响应时崩溃

- **文件**：`js/api.js` 第 18 行
- **问题**：服务器返回 500 错误（HTML 页面）时，`res.json()` 会抛出异常
- **修复**：
```js
let data;
try {
  data = await res.json();
} catch {
  data = { success: false, message: `服务器错误 (${res.status})` };
}
```

#### Bug 2: `request()` 在 401 时无 return

- **文件**：`js/api.js` 第 21-28 行
- **问题**：执行重定向后没有 return，调用方会继续执行后续逻辑
- **修复**：重定向后 `throw new Error('Unauthorized')`

#### Bug 13: 头像上传 base64 而非文件

- **文件**：`js/common.js` 第 961-982 行
- **问题**：`uploadLocal()` 直接发送 base64 data URL，而非先上传文件获取 URL
- **修复**：先调用 `API.upload.image(file)` 获取 URL，再传给 `updateProfile`

#### Bug 35: 点赞乐观更新无回滚

- **文件**：`pages/community.html` 第 296-309 行
- **问题**：先更新 UI 再调用 API，但 API 失败时没有回滚 UI 状态
- **修复**：添加 try-catch，失败时回滚

#### Bug 50: 删除帖子逻辑错误

- **文件**：`pages/my-posts.html` 第 281 行
- **问题**：`closeDeleteConfirm()` 将 `deletingPostId` 设为 null 后，再用它查找 DOM 元素会失败
- **修复**：先保存 `deletingPostId` 再调用 `closeDeleteConfirm()`

---

### 🟡 中严重性（15 个）

#### Bug 6: `initPage` 函数名冲突

- **文件**：`js/common.js` + 所有页面
- **问题**：`common.js` 和每个页面都定义了 `initPage` 并注册 `DOMContentLoaded`，导致被调用两次

#### Bug 9: `formatDate` 未处理无效日期

- **文件**：`js/common.js` 第 333-343 行
- **问题**：无效日期会显示 `NaN月NaN日`
- **修复**：添加 `if (isNaN(date.getTime())) return dateStr || '';`

#### Bug 17: 错误处理过于激进

- **文件**：`pages/home.html` 第 282-288 行
- **问题**：任何加载失败都会清除 token 并跳转登录页，包括网络超时
- **修复**：区分 401 和其他错误

#### Bug 18-19: `record.time` 和 `record.description` 可能为 undefined

- **文件**：`pages/home.html` 第 374 行、第 378 行
- **修复**：添加空值保护

#### Bug 25: `loadRecipes` 未处理 API 返回格式

- **文件**：`pages/discover.html` 第 290-291 行
- **修复**：添加防御性检查

#### Bug 28: `renderDesktopMacros` 没有空值保护

- **文件**：`pages/record.html` 第 476-505 行

#### Bug 34: `loadMorePosts` 未实现

- **文件**：`pages/community.html` 第 391 行
- **问题**：只显示 Toast，没有实际加载更多

#### Bug 37: `profile-avatar` 初始 src 为空

- **文件**：`pages/profile.html` 第 60 行
- **问题**：空 src 会导致 404 请求

#### Bug 39: `foodId` 可能为 null

- **文件**：`pages/food-detail.html` 第 251 行
- **修复**：开头检查 `if (!foodId) return;`

#### Bug 42: 移动端 tab 内容未填充

- **文件**：`pages/food-detail.html` 第 217 行
- **问题**：`content-recipe` 容器为空，移动端看不到制作步骤

#### Bug 45: `loadPlanData` DOM 选择器脆弱

- **文件**：`pages/ai-plan.html` 第 308-335 行
- **问题**：使用通用 CSS 选择器更新数据，容易匹配到错误元素
- **修复**：为元素添加专用 id

#### Bug 47: `meal.tags` 可能为 undefined

- **文件**：`pages/ai-plan.html` 第 411 行
- **修复**：使用 `(meal.tags || []).map(...)`

#### Bug 52: 多处 XSS 风险

- **文件**：`community.html`、`home.html`、`common.js`
- **问题**：用户输入直接插入 innerHTML，未做 HTML 转义
- **修复**：创建 `escapeHtml` 工具函数

#### Bug 53: `Promise.all` 任一失败则全部失败

- **文件**：`home.html`、`record.html`、`profile.html`
- **修复**：使用 `Promise.allSettled` 替代

---

### 🟢 低严重性（33 个）

| 编号 | 文件 | 问题 |
|------|------|------|
| 3 | api.js | 登录/注册重复存储 token |
| 4 | api.js | upload.image() 未使用统一错误处理 |
| 5 | components.js | renderEmptyState 中 actionUrl 为空时链接无效 |
| 7 | common.js | tooltip 定位使用 clientX/Y |
| 8 | common.js | tooltip 固定 id 可能重复 |
| 10 | common.js | formatNumber 未处理 null/undefined |
| 11 | common.js | AddRecordModal.onSearch this 指向 |
| 12 | common.js | Toast 提示文字不准确 |
| 14 | components.js | PostCard.render XSS 风险 |
| 15 | components.js | BarChart maxValue 可能为 NaN |
| 16 | components.js | RadarChart 不处理空数据 |
| 20 | home.html | initPage 被调用两次 |
| 21 | home.html | meal.id 直接插入 onclick |
| 22 | login.html | Toast 实现与 common.js 不一致 |
| 23 | login.html | 登录成功跳转不等待 |
| 24 | login.html | 已登录验证有竞态条件 |
| 26 | discover.html | 搜索大小写敏感 |
| 27 | discover.html | 手动 debounce |
| 29 | record.html | selectDay 中 records 未使用 |
| 30 | record.html | selectedDay 默认值与实际星期不对应 |
| 31 | record.html | chartHeight 可能为 0 |
| 32 | community.html | posts 变量名冲突 |
| 33 | community.html | fontVariationSettings 判断脆弱 |
| 36 | community.html | ESC 键未检查评论弹窗 |
| 38 | profile.html | achievements 可能不是数组 |
| 40 | food-detail.html | 硬编码 meal: 'lunch' |
| 41 | food-detail.html | addToRecord 重复调用 getDetail |
| 43 | ai-setup.html | 缺少登录检查 |
| 44 | ai-setup.html | API 失败时仍跳转 |
| 46 | ai-plan.html | goToFoodDetail 使用名称而非 ID |
| 48 | ai-plan.html | 底部导航高亮状态错误 |
| 49 | my-posts.html | posts.length 统计不准确 |
| 51 | 跨文件 | 重复大量 HTML 模板代码 |

---

## 三、汇总

### 按严重程度统计

| 严重程度 | 后端 | 前端 | 总计 |
|----------|------|------|------|
| 🔴 高 | 5 | 5 | **10** |
| 🟡 中 | 6 | 15 | **21** |
| 🟠 中低 | 5 | 0 | **5** |
| 🟢 低 | 4 | 33 | **37** |
| **总计** | **20** | **53** | **73** |

### 优先修复建议

#### P0 — 必须立即修复（影响核心功能）

1. **后端 Bug 1**：`get_json()` 返回 None 未处理 — 所有 POST 接口都可能崩溃
2. **后端 Bug 2-3**：点赞/评论/关注未校验存在性 — 会导致 500 错误
3. **后端 Bug 4**：`json.loads` 无异常保护 — 食物列表/详情可能崩溃
4. **前端 Bug 1**：`request()` 非 JSON 响应崩溃 — 服务器错误时前端白屏

#### P1 — 应该尽快修复（安全漏洞）

5. **后端 Bug 6**：Admin 后台无认证 — 任何人可操作后台数据
6. **后端 Bug 7-8**：Token 可预测 + SECRET_KEY 硬编码 — 安全风险
7. **前端 Bug 52**：多处 XSS 风险 — 可能被注入恶意脚本

#### P2 — 计划修复（体验优化）

8. **前端 Bug 6**：initPage 冲突 — API 被调用两次
9. **前端 Bug 17**：错误处理过于激进 — 网络波动被踢到登录页
10. **前端 Bug 34**：加载更多未实现 — 社区分页功能缺失

---

## 四、修复日志

| 日期 | 修复内容 |
|------|----------|
| 2026-06-02 | 初始检查报告生成 |
