# 海洋數據 API 功能說明

## 🌊 功能概述

這個功能可以根據前端提供的日期，返回該日期的海洋數據，包括：
- `sst_value`: 海表溫度值 (Sea Surface Temperature)
- `chl_value`: 葉綠素值 (Chlorophyll)  
- `ssha_value`: 海面高度異常值 (Sea Surface Height Anomaly)

## 📁 相關檔案

- `app/schemas/ocean_data.py` - 數據模型定義
- `app/services/ocean_data_service.py` - 數據處理服務
- `app/routers/ocean_data.py` - API 路由定義
- `test_ocean_data.py` - 簡化測試腳本
- `comprehensive_shark_ocean_features.csv` - 數據源檔案

## 🚀 API 端點

### 主要端點 (需要認證)

```
GET /api/v1/ocean-data/date/{date}
```
根據日期獲取海洋數據的平均值

**請求範例:**
```
GET /api/v1/ocean-data/date/2014-07-10
```

**響應範例:**
```json
{
  "date": "2014-07-10",
  "sst_value": 23.196178,
  "chl_value": 0.432361,
  "ssha_value": 0.073920,
  "data_count": 1
}
```

### 公開測試端點 (不需要認證)

```
GET /api/v1/ocean-data/public/date/{date}
```

### 其他端點

1. **POST 方式查詢**
   ```
   POST /api/v1/ocean-data/date
   Body: {"date": "2014-07-10"}
   ```

2. **獲取詳細數據**
   ```
   GET /api/v1/ocean-data/date/{date}/details
   ```
   返回該日期的所有原始記錄

3. **獲取統計摘要**
   ```
   GET /api/v1/ocean-data/date/{date}/summary
   ```
   返回該日期的統計信息（平均值、最大值、最小值等）

4. **日期範圍查詢**
   ```
   GET /api/v1/ocean-data/range?start_date=2014-07-10&end_date=2014-07-15
   ```

5. **獲取所有可用日期**
   ```
   GET /api/v1/ocean-data/dates
   ```

## 💻 使用方法

### 方法 1: 安裝完整依賴後啟動

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動 FastAPI 服務
python main.py

# 訪問 API 文檔
# http://localhost:8000/docs
```

### 方法 2: 使用簡化測試腳本

```bash
# 安裝基本依賴
pip install pandas

# 運行測試腳本
python test_ocean_data.py
```

### 方法 3: 直接測試（如果已安裝 pandas）

```python
from test_ocean_data import SimpleOceanDataTest
from datetime import date

# 創建測試實例
ocean_test = SimpleOceanDataTest()

# 查詢特定日期
result = ocean_test.get_data_by_date(date(2014, 7, 10))
print(result)
```

## 📊 數據說明

### 輸入
- **日期格式**: YYYY-MM-DD (例如: 2014-07-10)

### 輸出
- **sst_value**: 海表溫度值 (攝氏度)
- **chl_value**: 葉綠素濃度值  
- **ssha_value**: 海面高度異常值 (米)
- **data_count**: 該日期的數據筆數

### 數據處理
- 如果某個日期有多筆記錄，系統會自動計算平均值
- 如果某個日期沒有數據，相應的值會返回 `null`
- 所有數值都會四捨五入到小數點後 6 位

## 🔧 前端使用範例

### JavaScript/Fetch
```javascript
// 查詢指定日期的海洋數據
async function getOceanData(date) {
  const response = await fetch(`/api/v1/ocean-data/public/date/${date}`);
  const data = await response.json();
  
  console.log('海表溫度:', data.sst_value);
  console.log('葉綠素值:', data.chl_value);  
  console.log('海面高度異常:', data.ssha_value);
  
  return data;
}

// 使用範例
getOceanData('2014-07-10').then(data => {
  // 處理返回的數據
});
```

### Python/Requests
```python
import requests
from datetime import date

def get_ocean_data(target_date):
    url = f"http://localhost:8000/api/v1/ocean-data/public/date/{target_date}"
    response = requests.get(url)
    return response.json()

# 使用範例  
data = get_ocean_data('2014-07-10')
print(f"SST: {data['sst_value']}")
print(f"CHL: {data['chl_value']}")
print(f"SSHA: {data['ssha_value']}")
```

## 🐛 故障排除

1. **CSV 檔案找不到**
   - 確保 `comprehensive_shark_ocean_features - comprehensive_shark_ocean_features.csv` 在專案根目錄

2. **依賴安裝問題**
   - 運行 `pip install pandas numpy` 安裝必要依賴

3. **日期格式錯誤**
   - 確保使用 YYYY-MM-DD 格式，例如 2014-07-10

4. **沒有數據返回**
   - 檢查 CSV 檔案中是否有該日期的數據
   - 使用 `/api/v1/ocean-data/dates` 端點查看所有可用日期

## 📈 擴展功能

可以根據需要添加以下功能：
- 地理位置篩選 (經緯度範圍)
- 個體 ID 篩選
- 數據插值和預測
- 圖表可視化
- 數據匯出功能