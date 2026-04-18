#!/usr/bin/env python3
# 测试核心依赖包是否正常安装

import sys

def test_imports():
    """测试核心依赖包的导入"""
    packages = [
        'pandas',
        'numpy',
        'matplotlib',
        'vectorbt',
        'yfinance',
        'akshare',
        'tushare',
        'plotly',
        'PyQt6',
        'loguru',
        'scipy',
        'statsmodels',
        'causalml',
        'finrl',
        'gymnasium',
        'stable_baselines3',
        'torch',
        'torchvision',
        'torchaudio',
        'transformers',
        'whisper',
        'langchain',
        'gplearn',
        'deap',
        'lightgbm',
        'xgboost',
        'networkx',
        'joblib',
        'py_vollib',
        'quantlib',
        'jieba',
        'snownlp',
        'dotenv'
    ]
    
    print("Testing core dependencies...")
    print("=" * 50)
    
    success_count = 0
    failure_count = 0
    
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"✗ {package} failed to import: {e}")
            failure_count += 1
        except Exception as e:
            print(f"✗ {package} failed with error: {e}")
            failure_count += 1
    
    print("=" * 50)
    print(f"Summary: {success_count} successful, {failure_count} failed")
    
    if failure_count == 0:
        print("\n🎉 All dependencies are installed successfully!")
        return True
    else:
        print("\n❌ Some dependencies failed to install.")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\nTesting basic functionality...")
    print("=" * 50)
    
    try:
        import pandas as pd
        import numpy as np
        import vectorbt as vbt
        
        # 测试pandas
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        print(f"✓ pandas DataFrame created: {df.shape}")
        
        # 测试numpy
        arr = np.array([1, 2, 3, 4, 5])
        print(f"✓ numpy array created: {arr.shape}")
        
        # 测试vectorbt
        price = np.random.random(100)
        vbt_df = vbt.DataFrame({'price': price})
        print(f"✓ vectorbt DataFrame created: {vbt_df.shape}")
        
        print("\n🎉 Basic functionality test passed!")
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("Trae Solo GoldQuant Dependency Test")
    print("=" * 60)
    
    import_success = test_imports()
    function_success = test_basic_functionality()
    
    print("=" * 60)
    if import_success and function_success:
        print("\n✅ All tests passed! The environment is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)