"""
ML 數據預處理模組
包含數據清理、特徵工程和數據增強功能
"""

import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from sklearn.impute import SimpleImputer
from scipy.interpolate import griddata
from typing import Tuple, List, Optional
import os

class OceanDataProcessor:
    """海洋數據預處理器"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.features = [
            'Longitude', 'Latitude', 'SST_Value', 'SST_Gradient', 
            'CHL_Concentration', 'CHL_Gradient', 'SSHA_Value', 
            'Thermal_Front_Strength', 'Productivity_Index', 
            'SSHA_Gradient', 'dist_to_eddy_center_km', 
            'Daily_Movement_km', 'Day_of_Year'
        ]
        self.imputer = None
        
    def load_data(self) -> pd.DataFrame:
        """載入 CSV 數據"""
        try:
            df = pd.read_csv(self.csv_file_path)
            print(f"✅ 載入數據成功: {df.shape[0]} 行, {df.shape[1]} 列")
            return df
        except Exception as e:
            print(f"❌ 載入數據失敗: {e}")
            raise
    
    def filter_date_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """篩選日期範圍"""
        # 轉換日期格式
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 從數據中找到日期範圍
        start_date = df['Date'].min()
        end_date = df['Date'].max()
        
        print(f"📅 日期範圍: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        
        # 篩選日期範圍內的數據
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        print(f"📊 篩選後數據: {filtered_df.shape[0]} 行")
        return filtered_df
    
    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加時間特徵"""
        # 確保 Date 是 datetime 類型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 添加 Day_of_Year 特徵
        df['Day_of_Year'] = df['Date'].dt.dayofyear
        df['Month'] = df['Date'].dt.month
        
        print(f"✅ 添加時間特徵: Day_of_Year, Month")
        return df
    
    def filter_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """篩選需要的特徵"""
        # 檢查哪些特徵存在於數據中
        available_features = []
        for feat in self.features:
            if feat in df.columns:
                available_features.append(feat)
            else:
                print(f"⚠️ 特徵 {feat} 不存在於數據中")
        
        # 確保必要的欄位存在
        required_cols = ['Date', 'Longitude', 'Latitude', 'has_shark']
        for col in required_cols:
            if col not in df.columns:
                print(f"❌ 必要欄位 {col} 不存在")
                raise ValueError(f"必要欄位 {col} 不存在")
        
        self.features = available_features
        print(f"📋 使用特徵: {len(self.features)} 個")
        print(f"   {self.features}")
        
        return df
    
    def impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """填補缺失值"""
        # 使用中位數填補數值特徵的缺失值
        self.imputer = SimpleImputer(strategy='median')
        
        # 只對數值特徵進行填補
        numeric_features = [f for f in self.features if f in df.columns and df[f].dtype in ['float64', 'int64']]
        
        if numeric_features:
            print(f"🔧 填補 {len(numeric_features)} 個數值特徵的缺失值")
            imputed_data = self.imputer.fit_transform(df[numeric_features])
            df[numeric_features] = imputed_data
        
        return df
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """計算兩點間的距離（公里）"""
        R = 6371  # 地球半徑（公里）
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def augment_data(self, df: pd.DataFrame, grid_spacing: float = 0.09) -> pd.DataFrame:
        """數據增強：生成相隔10公里內無鯊魚的點"""
        print("🔄 開始數據增強...")
        
        # 獲取有鯊魚的座標
        shark_coords = df[df['has_shark'] == 1][['Longitude', 'Latitude']].values
        
        if len(shark_coords) == 0:
            print("⚠️ 沒有發現有鯊魚的數據點")
            return df
        
        # 獲取數據範圍
        lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
        lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
        
        print(f"📍 數據範圍: 經度 {lon_min:.2f} ~ {lon_max:.2f}, 緯度 {lat_min:.2f} ~ {lat_max:.2f}")
        
        # 生成網格點
        new_points = []
        total_points = 0
        valid_points = 0
        
        for lon in np.arange(lon_min, lon_max, grid_spacing):
            for lat in np.arange(lat_min, lat_max, grid_spacing):
                total_points += 1
                
                # 檢查是否距離任何鯊魚點超過10公里
                min_distance = min([
                    self.haversine_distance(lat, lon, shark_lat, shark_lon)
                    for shark_lon, shark_lat in shark_coords
                ])
                
                if min_distance > 10:  # 距離所有鯊魚點都超過10公里
                    new_points.append([lon, lat, 0])  # has_shark = 0
                    valid_points += 1
        
        print(f"🎯 生成 {valid_points}/{total_points} 個負樣本點")
        
        if not new_points:
            print("⚠️ 沒有生成新的負樣本點")
            return df
        
        # 創建新數據框
        new_df = pd.DataFrame(new_points, columns=['Longitude', 'Latitude', 'has_shark'])
        
        # 為新點插值其他特徵
        numeric_features = [f for f in self.features if f in df.columns and f not in ['Longitude', 'Latitude']]
        
        for feat in numeric_features:
            if feat in df.columns:
                try:
                    # 使用線性插值
                    interpolated_values = griddata(
                        (df['Longitude'].values, df['Latitude'].values), 
                        df[feat].values,
                        (new_df['Longitude'].values, new_df['Latitude'].values),
                        method='linear', 
                        fill_value=df[feat].median()
                    )
                    new_df[feat] = interpolated_values
                except Exception as e:
                    print(f"⚠️ 特徵 {feat} 插值失敗，使用中位數填充: {e}")
                    new_df[feat] = df[feat].median()
        
        # 設置日期（使用原數據的中位數日期）
        median_date = df['Date'].median()
        new_df['Date'] = median_date
        new_df['Month'] = median_date.month
        new_df['Day_of_Year'] = median_date.timetuple().tm_yday
        
        # 合併數據
        augmented_df = pd.concat([df, new_df], ignore_index=True)
        
        print(f"✅ 數據增強完成: {df.shape[0]} → {augmented_df.shape[0]} 行")
        return augmented_df
    
    def final_imputation(self, df: pd.DataFrame) -> pd.DataFrame:
        """最終填補處理"""
        print("🔧 進行最終數據清理...")
        
        # 重新填補所有特徵的缺失值
        numeric_features = [f for f in self.features if f in df.columns and df[f].dtype in ['float64', 'int64']]
        
        if numeric_features:
            final_imputer = SimpleImputer(strategy='median')
            imputed_data = final_imputer.fit_transform(df[numeric_features])
            df[numeric_features] = imputed_data
        
        return df
    
    def process_data(self, enable_augmentation: bool = True) -> pd.DataFrame:
        """完整的數據處理流程"""
        print("🚀 開始數據預處理...")
        
        # 1. 載入數據
        df = self.load_data()
        
        # 2. 篩選日期範圍
        df = self.filter_date_range(df)
        
        # 3. 篩選特徵
        df = self.filter_features(df)
        
        # 4. 添加時間特徵
        df = self.add_time_features(df)
        
        # 5. 填補缺失值
        df = self.impute_missing_values(df)
        
        # 6. 數據增強（可選）
        if enable_augmentation:
            df = self.augment_data(df)
        
        # 7. 最終填補
        df = self.final_imputation(df)
        
        print("✅ 數據預處理完成!")
        print(f"📊 最終數據形狀: {df.shape}")
        print(f"🦈 鯊魚樣本: {(df['has_shark'] == 1).sum()} 個")
        print(f"🌊 非鯊魚樣本: {(df['has_shark'] == 0).sum()} 個")
        
        return df
    
    def get_features_for_prediction(self, df: pd.DataFrame) -> np.ndarray:
        """獲取用於預測的特徵矩陣"""
        feature_cols = [f for f in self.features if f in df.columns]
        return df[feature_cols].values
    
    def get_labels(self, df: pd.DataFrame) -> np.ndarray:
        """獲取標籤"""
        return df['has_shark'].values


def process_uploaded_csv(csv_content: str, enable_augmentation: bool = False) -> Tuple[np.ndarray, List[str], Optional[str]]:
    """
    處理上傳的 CSV 內容
    
    Args:
        csv_content: CSV 內容字符串
        enable_augmentation: 是否啟用數據增強
    
    Returns:
        features: 特徵矩陣
        feature_names: 特徵名稱列表
        error: 錯誤信息（如果有）
    """
    try:
        import io
        
        # 將字符串轉換為 DataFrame
        df = pd.read_csv(io.StringIO(csv_content))
        
        # 創建臨時處理器
        processor = OceanDataProcessor("")
        processor.csv_file_path = None  # 不使用文件路径
        
        # 手動設置數據
        if 'Date' not in df.columns:
            # 如果沒有日期欄位，添加一個假的日期
            df['Date'] = pd.to_datetime('2024-01-01')
        
        if 'has_shark' not in df.columns:
            # 如果沒有鯊魚標籤，添加一個預設值
            df['has_shark'] = 0
        
        # 確保 Date 是 datetime 類型
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 篩選特徵
        df = processor.filter_features(df)
        
        # 添加時間特徵
        df = processor.add_time_features(df)
        
        # 填補缺失值
        df = processor.impute_missing_values(df)
        
        # 數據增強（可選）
        if enable_augmentation:
            df = processor.augment_data(df)
        
        # 最終填補
        df = processor.final_imputation(df)
        
        # 獲取特徵矩陣
        features = processor.get_features_for_prediction(df)
        feature_names = [f for f in processor.features if f in df.columns]
        
        return features, feature_names, None
        
    except Exception as e:
        return None, None, f"數據處理失敗: {str(e)}"


# 測試函數
def test_data_processing():
    """測試數據處理流程"""
    csv_file = "merged_shark_ocean_data.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ 檔案不存在: {csv_file}")
        return
    
    processor = OceanDataProcessor(csv_file)
    
    try:
        # 處理數據（不啟用數據增強以節省時間）
        processed_df = processor.process_data(enable_augmentation=False)
        
        print(f"\n📋 處理結果:")
        print(f"   數據形狀: {processed_df.shape}")
        print(f"   特徵數量: {len(processor.features)}")
        print(f"   特徵列表: {processor.features}")
        
        # 檢查標籤分佈
        label_counts = processed_df['has_shark'].value_counts()
        print(f"   標籤分佈: {dict(label_counts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


if __name__ == "__main__":
    test_data_processing()