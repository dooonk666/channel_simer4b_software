import os
import sys

# Add Qt bin directory to PATH
qt_bin_path = r"D:\python\Lib\site-packages\PyQt5\Qt5\bin"
if os.path.exists(qt_bin_path):
    os.environ['PATH'] = qt_bin_path + os.pathsep + os.environ['PATH']
    print(f"Added {qt_bin_path} to PATH")

try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 imported successfully!")
    app = QApplication(sys.argv)
    print("QApplication created successfully!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

