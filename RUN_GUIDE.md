# 程序运行快速指南

## 当前状态
✅ **24条多径支持已完成**
- UI界面支持1-24条多径选择
- 帧格式支持0-23路���索引
- 配置导入支持最多24个cluster

⚠️ **PyQt5 DLL加载问题需要修复**

## 立即运行程序

### 方法1：修复PyQt5后运行Python版本（推荐）

1. **运行自动修复脚本**
   ```powershell
   .\fix_pyqt5.bat
   ```
   脚本会检测问题并提示您下载���要的运行库

2. **手动安装Visual C++ Redistributable**
   - 下载并安装：https://aka.ms/vs/17/release/vc_redist.x64.exe
   - 重启计算机

3. **验证安装**
   ```powershell
   python test_pyqt5.py
   ```
   应该看到"PyQt5 imported successfully!"

4. **运行主程序**
   ```powershell
   python main.py
   ```

### 方法2：使用已编译的EXE（无需修复）

直接运行已编译的可执行文件：
```
.\channel_simer4b_software_V0.1\main.exe
```

或者：
```
.\build\main\main.exe
```

这个EXE文件已经包含了所有必要的依赖，不需要安装PyQt5。

## 测试24条多径功能

### 基本测试步骤
1. 启动程序
2. 点击"连接"菜单连接设备
3. 在主界面找到"多径号"下拉框
4. 验证下拉框包含1-24的选项
5. 选择任意多径（如路径24）
6. 设置时延、衰减等参数
7. 点击"确定"发送配置

### 配置文件测试
1. 准备一个包含24个cluster的JSON配置文件
2. 使用"导入配置"功能加载
3. 点击"应用配置"发送到设备
4. 检查状态栏是否显示"已应用配置：24个多径已发送"

## 常见问题

### Q: 运行python main.py时报DLL错误
**A:** 这是因为缺少Visual C++ Redistributable。请按照"方法1"的步骤安装，或使用"方法2"直接运行EXE。

### Q: 如何确认24条多径是否真的支持？
**A:** 
1. 打开UI，检查多径下拉框是否有1-24
2. 查看`24_MULTIPATH_SUMMARY.md`文件了解详细修改内容
3. 使用配置导入功能测试24个cluster

### Q: EXE文件在哪里？
**A:** 有两个位置：
- `.\channel_simer4b_software_V0.1\main.exe`
- `.\build\main\main.exe`

### Q: 程序运行正常，��IDE仍显示错误
**A:** IDE显示的是静态分析警告，不影响实际运行。只要PyQt5能正常导入，程序就能正常工作。

## 相关文档

- `PYQT5_DLL_FIX.md` - PyQt5 DLL问题详细解决方案
- `24_MULTIPATH_SUMMARY.md` - 24条多径支持完成总结
- `QUICK_START_GUIDE.md` - 程序使用快速入门
- `CONFIG_IMPORT_README.md` - 配置导入功能说明
- `TESTING_CHECKLIST.md` - 测试检查清单

## 技术支持

如果以上方法都无法解决问题：
1. 检查Python版本（推荐3.8-3.11）
2. 检查是否为64位Windows系统
3. 尝试使用Anaconda环境：`conda install pyqt`
4. 查看`PYQT5_DLL_FIX.md`获取更多解决方案

## 下一步

程序已经完全支持24条多径，您可以：
1. 修复PyQt5 DLL问题后正常使用
2. 或者直接使用EXE版本
3. 按需测试24条多径功能
4. 根据实际需求调整配置

---

**最后更新：** 2026-01-20
**当前版本：** V0.1 (支持24条多径)

