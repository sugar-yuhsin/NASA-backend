# 🌊 NASA 海洋數據查詢功能

## ✅ 功能已完成！

我已經為你創建了一個完整的海洋數據查詢功能，可以根據前端提供的日期返回該日期的海洋值。

## 📁 實現檔案

### 1. 簡化版命令行工具
- **檔案**: `simple_ocean_query.py`  
- **功能**: 直接從命令行查詢海洋數據
- **使用**: `python simple_ocean_query.py`

### 2. 簡化版 FastAPI 服務
- **檔案**: `simple_api.py`
- **功能**: HTTP API 服務，支援 GET 和 POST 請求
- **使用**: `python simple_api.py`

## 🚀 如何使用

### 方法 1: 命令行查詢

```bash
# 進入 conda 環境
conda activate NASAhack

# 運行查詢工具
python simple_ocean_query.py

# 輸入日期進行查詢，例如: 2014-07-10
```

### 方法 2: API 服務

```bash
# 啟動 API 服務
conda activate NASAhack
python simple_api.py

# 服務將在 http://localhost:8000 啟動
# 查看 API 文檔: http://localhost:8000/docs
```

## 📡 API 端點

### GET 方式查詢
```
GET /ocean-data/{date}

範例: http://localhost:8000/ocean-data/2014-07-10
```

### POST 方式查詢
```
POST /ocean-data
Content-Type: application/json

{
  "date": "2014-07-10"
}
```

### 其他端點
- `GET /` - 根端點和說明
- `GET /available-dates` - 獲取可用日期列表
- `GET /health` - 健康檢查
- `GET /docs` - API 文檔

## 📊 返回數據格式

```json
{
  "date": "2014-07-10",
  "sst_value": 23.138945,
  "chl_value": 0.569743,
  "ssha_value": 0.07392,
  "data_count": 14,
  "message": "查詢成功"
}
```

### 字段說明
- `date`: 查詢的日期
- `sst_value`: 海表溫度值 (Sea Surface Temperature)
- `chl_value`: 葉綠素值 (Chlorophyll)
- `ssha_value`: 海面高度異常值 (Sea Surface Height Anomaly)
- `data_count`: 該日期的數據筆數（如果有多筆會計算平均值）
- `message`: 查詢狀態信息

## 🔧 前端集成範例

### JavaScript/Fetch
```javascript
async function getOceanData(date) {
  try {
    const response = await fetch(`http://localhost:8000/ocean-data/${date}`);
    const data = await response.json();
    
    console.log('海表溫度:', data.sst_value);
    console.log('葉綠素值:', data.chl_value);
    console.log('海面高度異常:', data.ssha_value);
    
    return data;
  } catch (error) {
    console.error('查詢失敗:', error);
  }
}

// 使用範例
getOceanData('2014-07-10').then(data => {
  // 處理返回的數據
  if (data.sst_value !== null) {
    document.getElementById('sst').textContent = data.sst_value;
  }
});
```

### Python/Requests
```python
import requests

def get_ocean_data(date):
    url = f"http://localhost:8000/ocean-data/{date}"
    response = requests.get(url)
    return response.json()

# 使用範例
data = get_ocean_data('2014-07-10')
print(f"SST: {data['sst_value']}")
print(f"CHL: {data['chl_value']}")
print(f"SSHA: {data['ssha_value']}")
```

### curl 命令
```bash
# GET 查詢
curl http://localhost:8000/ocean-data/2014-07-10

# POST 查詢
curl -X POST http://localhost:8000/ocean-data \
  -H "Content-Type: application/json" \
  -d '{"date": "2014-07-10"}'
```

## ✨ 特色功能

1. **簡單易用**: 不需要複雜的認證，直接查詢
2. **多種方式**: 支援 GET 和 POST 兩種查詢方式
3. **自動平均**: 如果同一天有多筆記錄，自動計算平均值
4. **錯誤處理**: 完善的錯誤處理和返回信息
5. **日期驗證**: 自動驗證日期格式
6. **API 文檔**: 內建 Swagger UI 文檔

## 📅 可用日期範圍

根據你的 CSV 檔案，可用的日期從 **2014-07-10** 開始。你可以使用 `/available-dates` 端點查看所有可用日期。

## 🐛 故障排除

### 問題 1: CSV 檔案找不到
- 確保 `comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv` 在專案根目錄

### 問題 2: API 無法啟動
- 確保在 conda 環境中：`conda activate NASAhack`
- 檢查埠口是否被佔用：`lsof -i :8000`

### 問題 3: 查詢結果為空
- 檢查日期格式是否正確 (YYYY-MM-DD)
- 使用 `/available-dates` 確認該日期是否有數據

## 🎯 總結

你現在有了一個完整的海洋數據查詢功能：

1. ✅ **前端發送日期** → API 接收
2. ✅ **後端查詢 CSV** → 找到對應日期數據  
3. ✅ **計算平均值** → 如果有多筆記錄
4. ✅ **返回三個值** → sst_value, chl_value, ssha_value

這個實現非常簡潔且實用，完全滿足你的需求！ 🚀