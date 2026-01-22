# PyQt5 DLL加载错误解决方案

## 错误信息
```
ImportError: DLL load failed while importing QtWidgets: 找不到指定的程序。
```

## 原因
这个错误通常是因为系统缺少Microsoft Visual C++ Redistributable运行库。

## 解决方案

### 方案1：安装Microsoft Visual C++ Redistributable（推荐）
1. 下载并安装以下两个版本的Visual C++ Redistributable：
   - **Visual C++ 2015-2022 Redistributable (x64)**
     - 下载链接：https://aka.ms/vs/17/release/vc_redist.x64.exe
   - **Visual C++ 2013 Redistributable (x64)**
     - 下载链接：https://aka.ms/highdpimfc2013x64enu

2. 安装完成后重启计算机

3. 运行程序：
   ```powershell
   python main.py
   ```

### 方案2：使用已编译的exe文件
如果您不想安装Visual C++ Redistributable，可以使用已编译的exe版本：
```
channel_simer4b_software_V0.1\main.exe
```

### 方案3：使用conda环境（如果您使用Anaconda）
```powershell
conda install pyqt
```
Conda会自动处理所有依赖关系。

### 方案4：检查并修复PyQt5安装
```powershell
pip uninstall PyQt5 PyQt5-sip PyQt5-Qt5 -y
pip install PyQt5==5.15.9 --no-cache-dir
```

## 验证安装
运行以下��令测试PyQt5是否正常工作：
```powershell
python test_pyqt5.py
```

如果看到"PyQt5 imported successfully!"和"QApplication created successfully!"，说明安装成功。

## 24条多径支持说明
本软件已完整支持24条多径：
- UI界面comboBox_path已包含1-24的选项
- 帧格式生成函数支持0-23索引（24条路径）
- 配置导入功能支持最多24个cluster
- 所有多径参数（时延、衰减、瑞利衰落等）都支持24条

## 需要帮助？
如果上述方案都无法解决问题，请检查：
1. Python版本是否为3.7-3.11（推荐3.8或3.9）
2. 系统是否为64位Windows
3. 是否有管理员权限安装软件

