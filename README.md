# NASA Hackathon FastAPI 專案

🚀 這是一個基於 FastAPI 的 NASA 黑客松專案，提供了完整的 RESTful API 架構和現代化的開發工具鏈。

## 🌟 特色功能

- **現代化框架**: 使用 FastAPI 構建高性能 API
- **自動文檔**: 內建 Swagger UI 和 ReDoc 文檔
- **身份驗證**: JWT 基礎的用戶認證系統
- **資料驗證**: 使用 Pydantic 進行數據驗證
- **資料庫支持**: SQLAlchemy ORM + PostgreSQL
- **快取系統**: Redis 快取支持
- **容器化**: Docker 和 Docker Compose 配置
- **代碼品質**: 預配置的 linting 和格式化工具
- **測試框架**: pytest 測試套件

## 📁 專案結構

```
NASAhackthon/
├── app/                        # 主應用程式目錄
│   ├── __init__.py
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   └── config.py          # 應用程式設定
│   ├── models/                 # 資料庫模型
│   │   └── __init__.py
│   ├── schemas/                # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── auth.py            # 認證相關模型
│   │   ├── item.py            # 項目模型
│   │   └── user.py            # 用戶模型
│   ├── routers/                # API 路由
│   │   ├── __init__.py        # 主路由註冊
│   │   ├── auth.py            # 認證路由
│   │   ├── items.py           # 項目管理路由
│   │   └── users.py           # 用戶管理路由
│   └── services/               # 業務邏輯服務
│       ├── __init__.py
│       └── auth_service.py    # 認證服務
├── tests/                      # 測試文件
│   └── __init__.py
├── main.py                     # 應用程式入口
├── requirements.txt            # Python 依賴
├── pyproject.toml             # 專案配置
├── Dockerfile                 # Docker 鏡像配置
├── docker-compose.yml         # 生產環境 Docker 配置
├── docker-compose.dev.yml     # 開發環境 Docker 配置
├── .env.example              # 環境變數範例
├── .env                      # 環境變數配置
└── README.md                 # 專案說明文檔
```

## 🚀 快速開始

### 前置需求

- Python 3.8+
- Docker & Docker Compose (可選)
- PostgreSQL (如果不使用 Docker)
- Redis (如果不使用 Docker)

### 本地開發

1. **克隆專案**
   ```bash
   git clone <your-repo-url>
   cd NASAhackthon
   ```

2. **創建虛擬環境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\\Scripts\\activate  # Windows
   ```

3. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

4. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，設定你的配置
   ```

5. **啟動應用程式**
   ```bash
   python main.py
   ```

6. **訪問 API 文檔**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 使用 Docker 開發

1. **克隆專案**
   ```bash
   git clone <your-repo-url>
   cd NASAhackthon
   ```

2. **啟動開發環境**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. **訪問應用程式**
   - API: http://localhost:8000
   - API 文檔: http://localhost:8000/docs

## 📚 API 文檔

### 主要端點

- `GET /` - 根端點，健康檢查
- `GET /health` - 詳細健康檢查
- `GET /docs` - Swagger UI 文檔
- `GET /redoc` - ReDoc 文檔

### 認證相關

- `POST /api/v1/auth/register` - 用戶註冊
- `POST /api/v1/auth/login` - 用戶登入
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 獲取當前用戶信息
- `POST /api/v1/auth/logout` - 用戶登出

### 用戶管理

- `GET /api/v1/users/` - 獲取用戶列表
- `GET /api/v1/users/{id}` - 獲取指定用戶
- `POST /api/v1/users/` - 創建用戶
- `PUT /api/v1/users/{id}` - 更新用戶
- `DELETE /api/v1/users/{id}` - 刪除用戶

### 項目管理

- `GET /api/v1/items/` - 獲取項目列表
- `GET /api/v1/items/{id}` - 獲取指定項目
- `POST /api/v1/items/` - 創建項目
- `PUT /api/v1/items/{id}` - 更新項目
- `DELETE /api/v1/items/{id}` - 刪除項目

## 🔧 開發工具

### 代碼品質

```bash
# 格式化代碼
black .

# 整理導入
isort .

# 代碼檢查
flake8

# 類型檢查
mypy app
```

### 測試

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_auth.py

# 生成覆蓋率報告
pytest --cov=app tests/
```

## 🐳 部署

### 生產環境部署

1. **準備環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env，設定生產環境配置
   ```

2. **使用 Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

3. **設定反向代理**
   - 配置 Nginx 或其他反向代理
   - 設定 SSL 憑證

### 環境變數說明

| 變數名稱 | 說明 | 預設值 |
|---------|------|-------|
| `DEBUG` | 除錯模式 | `false` |
| `SECRET_KEY` | JWT 密鑰 | 需要設定 |
| `DATABASE_URL` | 資料庫連接 URL | PostgreSQL |
| `REDIS_URL` | Redis 連接 URL | `redis://localhost:6379/0` |
| `NASA_API_KEY` | NASA API 金鑰 | `DEMO_KEY` |

## 🔐 安全性

- JWT 令牌驗證
- 密碼雜湊 (bcrypt)
- CORS 保護
- 輸入驗證
- SQL 注入防護

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 許可證

此專案採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件

## 🆘 支持

如果你有任何問題或建議，請：

1. 查看 [Issues](https://github.com/your-username/nasa-hackathon/issues)
2. 創建新的 Issue
3. 聯繫專案維護者

## 🙏 致謝

- [FastAPI](https://fastapi.tiangolo.com/) - 現代、快速的 Python Web 框架
- [NASA Open Data Portal](https://data.nasa.gov/) - 資料來源
- 所有貢獻者和支持者

---

**祝你的 NASA 黑客松專案開發順利！** 🚀🌟# NASA-backend
