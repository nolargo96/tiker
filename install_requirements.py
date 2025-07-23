#!/usr/bin/env python3
"""
Tiker Dashboard 依存パッケージインストーラー
"""

import subprocess
import sys
import importlib.util

def check_package(package_name):
    """パッケージがインストールされているか確認"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    """パッケージをインストール"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package_name}")
        return False

def main():
    print("=" * 60)
    print("Tiker Dashboard - Package Installer")
    print("=" * 60)
    print()
    
    # 必要なパッケージリスト
    required_packages = {
        'streamlit': 'Streamlit (Web framework)',
        'pandas': 'Pandas (Data analysis)',
        'numpy': 'NumPy (Numerical computing)',
        'yfinance': 'yFinance (Stock data)',
        'plotly': 'Plotly (Interactive charts)',
        'xlsxwriter': 'XlsxWriter (Excel export)',
        'reportlab': 'ReportLab (PDF generation)',
        'matplotlib': 'Matplotlib (Charts)',
        'seaborn': 'Seaborn (Statistical plots)',
        'PyYAML': 'PyYAML (Configuration)',
        'pytest': 'Pytest (Testing)',
        'mypy': 'MyPy (Type checking)',
        'black': 'Black (Code formatter)',
        'flake8': 'Flake8 (Linter)'
    }
    
    # pipの確認
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except:
        print("ERROR: pip is not installed!")
        print("Please install pip first: https://pip.pypa.io/en/stable/installation/")
        sys.exit(1)
    
    print("Checking installed packages...")
    print("-" * 60)
    
    missing_packages = []
    installed_packages = []
    
    for package, description in required_packages.items():
        if check_package(package):
            installed_packages.append(package)
            print(f"✓ {package:<15} - {description} (already installed)")
        else:
            missing_packages.append((package, description))
            print(f"✗ {package:<15} - {description} (missing)")
    
    print()
    
    if not missing_packages:
        print("All packages are already installed!")
        print()
        print("You can now run the dashboard:")
        print("  streamlit run dashboard_pro.py")
        return
    
    print(f"Found {len(missing_packages)} missing packages")
    print()
    
    # インストール確認
    response = input("Do you want to install missing packages? (y/n): ")
    if response.lower() != 'y':
        print("Installation cancelled")
        return
    
    print()
    print("Installing missing packages...")
    print("-" * 60)
    
    failed_packages = []
    
    for package, description in missing_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print()
    print("=" * 60)
    print("Installation Summary")
    print("=" * 60)
    print(f"Total packages: {len(required_packages)}")
    print(f"Already installed: {len(installed_packages)}")
    print(f"Newly installed: {len(missing_packages) - len(failed_packages)}")
    print(f"Failed: {len(failed_packages)}")
    
    if failed_packages:
        print()
        print("Failed packages:")
        for package in failed_packages:
            print(f"  - {package}")
        print()
        print("Try installing these manually:")
        print(f"  pip install {' '.join(failed_packages)}")
    else:
        print()
        print("✓ All packages installed successfully!")
        print()
        print("You can now run the dashboard:")
        print("  streamlit run dashboard_pro.py")
        print()
        print("Or use the batch file:")
        print("  run_dashboard_pro.bat")

if __name__ == "__main__":
    main()