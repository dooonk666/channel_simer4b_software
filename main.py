import os
import sys

# Fix PyQt5 DLL loading issue by adding Qt bin directory to PATH
try:
    qt_bin_path = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "PyQt5", "Qt5", "bin")
    if os.path.exists(qt_bin_path):
        os.environ['PATH'] = qt_bin_path + os.pathsep + os.environ.get('PATH', '')
except:
    pass

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWidgets import *
from PyQt5 import QtCore,QtGui
from PyQt5.QtGui import QPainter, QPen
#from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
import socket
import math
import binascii
import json

from UI.MainWindow import Ui_MainWindow
from UI.simulator_figure import Ui_simulator_figure
from Rayl_PSD_related_cal import *

CLK_TS=5
FREQ_UNIT=1/21.47483648
SS_FREQ_UNIT=1/71.58278827  #内置信号源频率单位

CLK_F=1/CLK_TS*1000000  #kHz
FS_MAX=int(2**27*FREQ_UNIT*0.99)

#产生参数子帧
def gen_subframe(ID, Bytes_num, port_in, port_out, path, param_value):
    Bytes= b''
    Bytes = Bytes + ID.to_bytes(1, byteorder='little')
    Bytes = Bytes + Bytes_num.to_bytes(1, byteorder='little')
    Bytes = Bytes + (port_in * 16 + port_out).to_bytes(1, byteorder='little')
    Bytes = Bytes + path.to_bytes(1, byteorder='little')

    if (Bytes_num == 1 or 2 or 4):
        if param_value>0:
            Bytes = Bytes + param_value.to_bytes(Bytes_num, byteorder='little', signed=False)
        else:
            Bytes = Bytes + param_value.to_bytes(Bytes_num, byteorder='little', signed=True)
    else:
        print('Bytes_num unexpect!')


    return Bytes

def data_to_dB(data, type, No):
    if type==0:  #输入功率数据转换
        aa=0 + math.log10(data/8388608)*10 if data>0 else None #8380418=2*(2^15-1)^2=0dBFs    #计算log(零、负数)会返回None
    elif type==1 or type==2:  #输出功率数据转换
        aa = 0 + math.log10(data / 2147483648) * 10 if data>0 else None #2147352578=2*(2^31-1)^2=0dBFs
    else:
        aa = None
    return aa


class MainForm(QMainWindow, Ui_MainWindow):
    sig_change_special_line=pyqtSignal(list)

    def __init__(self):
        super(MainForm, self).__init__()

        self.setupUi(self)
        self.label_input_Lvs = [self.label_input_Lv, self.label_input_Lv_2, self.label_input_Lv_3, self.label_input_Lv_4, self.label_input_Lv_5, self.label_input_Lv_6, self.label_input_Lv_7, self.label_input_Lv_8]
        self.label_input_Ps = [self.label_input_P, self.label_input_P_2, self.label_input_P_3, self.label_input_P_4, self.label_input_P_5, self.label_input_P_6, self.label_input_P_7, self.label_input_P_8]
        self.label_output_Ps = [self.label_output_P, self.label_output_P_2, self.label_output_P_3, self.label_output_P_4, self.label_output_P_5, self.label_output_P_6, self.label_output_P_7, self.label_output_P_8]
        self.label_output_P_with_noises = [self.label_output_P_with_noise, self.label_output_P_with_noise_2, self.label_output_P_with_noise_3, self.label_output_P_with_noise_4, self.label_output_P_with_noise_5, self.label_output_P_with_noise_6, self.label_output_P_with_noise_7, self.label_output_P_with_noise_8]
        self.label_output_Lvs = [self.label_output_Lv, self.label_output_Lv_2, self.label_output_Lv_3, self.label_output_Lv_4, self.label_output_Lv_5, self.label_output_Lv_6, self.label_output_Lv_7, self.label_output_Lv_8]
        self.action.triggered.connect(self.TCP_connect_switch)

        self.comboBox_chan_input.currentIndexChanged.connect(self.change_special_line)
        self.comboBox_chan_output.currentIndexChanged.connect(self.change_special_line)



    def change_special_line(self): # 改变当前所选择信道输入和输出后，变示意图
        a=self.comboBox_chan_input.currentIndex()
        b=self.comboBox_chan_output.currentIndex()
        list0=[a,b]
        self.sig_change_special_line.emit(list0)


    def TCP_connect_switch(self):   #TCP连接开关
        if TCP_socket.TCP_connected:
            if Thread_net_receive0.isRunning() == True:   #显示模块还在运行，则先将其关闭再断网
                Thread_net_receive0.terminate()
                clear_info_display()
                self.action_3.setText('开启')

            TCP_socket.my_socket.close()
            TCP_socket.TCP_connected =False
            self.action.setText('连接')
            self.statusbar.showMessage('连接已断开...', 3000)
            return 0

        #  连接
        TCP_socket.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.my_socket.settimeout(3)         # 设置超时时间，让它不会连不上一直卡着
        try:
            TCP_socket.my_socket.connect(('192.168.1.10', 7))
        except:
            self.statusbar.showMessage('连接建立失败...', 3000)
            return -1
        # send_data = b'\xfd\xb1\x85\x40\x05\x00\x0e\x01\x00\x00\x03\xae\x86'  #向设备请求1个回传
        # TCP_socket.my_socket.send(send_data)
        # recv_data = TCP_socket.my_socket.recv(1024)

        self.action.setText('断开')
        self.statusbar.showMessage('连接建立...', 3000)
        TCP_socket.TCP_connected = True

        Thread_net_receive0.start()

class TCP_socket():
    my_socket = None
    def __init__(self):
        self.TCP_connected = False



class Thread_net_receive(QThread):
    s_data_recv = pyqtSignal(list)
    net_received=False
    def __int__(self):
        super().__init__()

    def run(self):
        while True:
            try:
                recv_data = TCP_socket.my_socket.recv(1024)  # 接收回传
                ssss=[recv_data]
                self.s_data_recv.emit(ssss)
                self.net_received = 0
            except:
                self.net_received = 1
    # 将信息帧解出信息并显示
def decode_Info_Frame_and_show(aa):
    recv_data=aa[0]

    if (recv_data[0:4] == b'\xfd\xb1\x85\x41'): #信息帧帧头
        Bytes=recv_data[0:]
        if(len(Bytes)<139):   #要求数量满足
            return -1
        ## AD超限
        which_Bytes=6
        Bytes_watch = Bytes[which_Bytes]
        for i in range(8):
            bit_ = (Bytes_watch>>i) & 1
            print("AD%d超限:"%i+  "%d"%bit_,  end="  ")
        print('')  # 回车

        ## 输入电平
        which_Bytes = 7
        for i in range(8):

            Bytes_watch = Bytes[which_Bytes: (which_Bytes+2)]
            which_Bytes = which_Bytes + 2

            data_=int.from_bytes(Bytes_watch,byteorder='little', signed=False)
            percent=data_ / 2048 * 100
            print("输入%d电平:" % i + "%0.2f%%" % percent, end="  ")

            if i<8:
                win.label_input_Lvs[i].setText("%0.2f%%"% percent)
        print('')  # 回车

        ## 输入功率
        which_Bytes = 23
        for i in range(8):
            Bytes_watch = Bytes[which_Bytes: (which_Bytes+4)]
            which_Bytes = which_Bytes + 4

            data_=int.from_bytes(Bytes_watch,byteorder='little', signed=False)
            print("输入%d功率:" % i + "%d" % data_, end="  ")


            aa=data_to_dB(data_,0,0)
            if i<8:
                if aa!=None:
                    win.label_input_Ps[i].setText("%0.2f dBFS" % aa)
                else:
                    win.label_input_Ps[i].setText("--")
        print('')  # 回车

        ## 合路溢出
        which_Bytes=55
        Bytes_watch = Bytes[which_Bytes]
        for i in range(8):
            bit_ = (Bytes_watch>>i) & 1
            # print("合路%d溢出:"%i+  "%d"%bit_,  end="  ")

        ## AWGN溢出
        which_Bytes=56
        Bytes_watch = Bytes[which_Bytes]
        for i in range(8):
            bit_ = (Bytes_watch>>i) & 1
            # print("AWGN%d溢出:"%i+  "%d"%bit_,  end="  ")

        ## 输出功率（无噪声）
        which_Bytes = 57
        for i in range(8):
            Bytes_watch = Bytes[which_Bytes: (which_Bytes+4)]
            which_Bytes = which_Bytes + 4

            data_=int.from_bytes(Bytes_watch,byteorder='little', signed=False)
            print("输出%d功率（无噪声）:" % i + "%d" % data_, end="  ")
            if i < 8:
                aa=data_to_dB(data_,1,0)
                if aa != None:
                    win.label_output_Ps[i].setText("%0.2f dBFS" % aa)
                else:
                    win.label_output_Ps[i].setText("--")
        print('')  # 回车
        ## 输出功率（有噪声）
        which_Bytes = 89
        for i in range(8):
            Bytes_watch = Bytes[which_Bytes: (which_Bytes+4)]
            which_Bytes = which_Bytes + 4

            data_=int.from_bytes(Bytes_watch,byteorder='little', signed=False)
            print("输出%d功率（有噪声）:" % i + "%d" % data_, end="  ")
            if i < 8:
                aa=data_to_dB(data_,1,0)
                if aa != None:
                    win.label_output_P_with_noises[i].setText("%0.2f dBFS" % aa)
                else:
                    win.label_output_P_with_noises[i].setText("--")
        print('')  # 回车
        ## 输出电平
        which_Bytes = 121
        for i in range(8):
            Bytes_watch = Bytes[which_Bytes: (which_Bytes+2)]
            which_Bytes = which_Bytes + 2

            data_=int.from_bytes(Bytes_watch,byteorder='little', signed=False)
            percent=data_ / 32768 * 100
            # print("输出%d电平:" % i + "%0.0f%%" % percent, end="  ")
            if i < 8:
                win.label_output_Lvs[i].setText("%0.2f%%" % percent)

        print('')
    elif (recv_data[0:4] == b'\xfd\xb1\x85\x50'): #串口上传帧帧头


        uart_data_num=int(recv_data[4])
        uart_data = recv_data[5: 5+uart_data_num]
        hex_string = binascii.hexlify(uart_data)
        hex_string=hex_string.decode()
        hex_string = ' '.join([hex_string[i:i + 2] for i in range(0, len(hex_string), 2)])#每两个字符加空格
        win.label_uart_rx.setText(hex_string)
        win.statusbar.showMessage('串口接收！', 1000)

##加帧头帧长帧尾
def Frame_forming(Bytes):

    # 加帧长
    frame_Bytes_num = len(Bytes)
    aaa = frame_Bytes_num.to_bytes(2, byteorder='little')
    Bytes = aaa + Bytes
    # 加帧头
    Bytes = frame_head + Bytes
    # 加帧尾
    Bytes = Bytes + frame_end

    return Bytes

def make_send_channel_delay_ctrl():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1
    port_in=win.comboBox_chan_input.currentIndex()
    ####################################################################
    port_out=win.comboBox_chan_output.currentIndex()
    ####################################################################
    channel_delay=win.LE_channel_delay.text()
    channel_delay=float(channel_delay)   #ns
    channel_delay=round(channel_delay/CLK_TS)
    channel_delay=int(channel_delay)
    Bytes = b''

    ID = 31  # 信道时延
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, 0, channel_delay)
    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_path_ctrl():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    port_in=win.comboBox_chan_input.currentIndex()
    ####################################################################
    port_out=win.comboBox_chan_output.currentIndex()
    ####################################################################
    which_path=win.comboBox_path.currentIndex()
    ####################################################################
    path_delay=win.LE_delay.text()
    path_delay=float(path_delay)   #ns
    path_delay=round(path_delay/CLK_TS)
    path_delay=int(path_delay)
    ####################################################################
    path_small_delay=win.comboBox_small_delay.currentIndex()

    ####################################################################
    fs=win.LE_fs.text()
    fs=float(fs)
    if fs > FS_MAX or fs < -FS_MAX :
        win.statusbar.showMessage('设置失败：频移数值超限', 3000)
        return -1
    fs= round( fs / FREQ_UNIT )
    fs = int(fs)
    ####################################################################
    atten=win.LE_atten.text()
    atten=float(atten)    #dB
    k= round( 10**(-atten/10/2)* (2**15) )
    k=int(k)

    ####################################################################
    phase_bias=win.LE_phase_bias.text()
    phase_bias = float(phase_bias)
    if phase_bias > 1 or phase_bias < 0:
        win.statusbar.showMessage('设置失败：相偏必须0~1', 3000)
        return -1
    phase_bias = round(phase_bias *4096)
    if phase_bias>4095:
        phase_bias = 4095
    phase_bias=int(phase_bias)

    ####################################################################
    Rayl_spread=win.LE_Rayl_spread.text()
    Rayl_spread=float(Rayl_spread)
    if Rayl_spread<=0:
        win.statusbar.showMessage('设置失败：多普勒扩展应大于0', 3000)
        return -1
    bandwidth=Rayl_spread/ (CLK_F/64/2)

    ####################################################################
    Rayl_type=win.comboBox_Rayl_type.currentIndex()


    if win.checkBox_path_en.isChecked():
        path_en=1
    else:
        path_en=0

    if win.checkBox_Rayl_en.isChecked():
        Rayl_en=1
    else:
        Rayl_en=0


    Bytes = b''

    ID = 2  # 多径使能
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, path_en)
    ID = 3  # 多径时延
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, path_delay)
    ID = 34  # 分数时延
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, path_small_delay)
    ID = 4  # 多径频移
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, fs)
    ID = 7  # 多径幅值衰减
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, k)
    ID = 32 #相偏
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, phase_bias)
    ID = 5  # 多径瑞利衰落使能
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, Rayl_en)
    #得到多普勒谱频域滤波系数
    if Rayl_en==1:
        Rayl_data=gen_Rayl_PSD_param(Rayl_type, bandwidth, 0.2)
        ID=6
        Bytes=Bytes + ID.to_bytes(1, byteorder='little')  #ID=6
        Bytes = Bytes + b'\x00'      #长度无所谓
        Bytes = Bytes + (port_in * 16 + port_out).to_bytes(1, byteorder='little')
        Bytes = Bytes + which_path.to_bytes(1, byteorder='little')
        for data_i in Rayl_data:
            Bytes = Bytes + data_i.to_bytes(2, byteorder='little', signed=True)

    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)
    if path_en:
        widget0.add_line([port_in, port_out])
    else:
        widget0.delete_line([port_in, port_out])

def make_send_f_sweep_ctrl():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    port_in=win.comboBox_chan_input.currentIndex()
    ####################################################################
    port_out=win.comboBox_chan_output.currentIndex()
    ####################################################################
    which_path=win.comboBox_path.currentIndex()
    ####################################################################

    fs_start=win.LE_fs_start.text()
    fs_start=float(fs_start)
    fs_start= round( fs_start / FREQ_UNIT )
    fs_start = int(fs_start)

    ####################################################################
    fs_end=win.LE_fs_end.text()
    fs_end = float(fs_end)
    fs_end= round( fs_end / FREQ_UNIT )
    fs_end = int(fs_end)
    ####################################################################
    fs_speed=win.LE_fs_speed.text()
    fs_speed = float(fs_speed)
    fs_speed= round( fs_speed /FREQ_UNIT * (2**15) / 1000000)
    fs_speed = int(fs_speed)
    ####################################################################
    fs_ctrl=win.comboBox_fs_ctrl.currentIndex()
    ####################################################################

    Bytes = b''

    ID = 23  # 扫频起点
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, fs_start)
    ID = 17  # 扫频终点
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, fs_end)
    ID = 18  # 扫频速度
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, fs_speed)
    ID = 19  # 扫频模式
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, fs_ctrl)


    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)
    #send_f_sweep_restart()                              ##########################

def make_send_output_ctrl():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    port_out = win.comboBox_output.currentIndex()

    output_atten=win.LE_output_atten.text()
    output_atten=float(output_atten)
    output_k = round(10 ** (-output_atten / 10 / 2) * (2 ** 14))
    output_k = int(output_k)

    if win.checkBox_output_en.isChecked():
        output_en=1  # 输出使能
    else:
        output_en=0

    if win.checkBox_AWGN_en.isChecked():
        noise_en=1  # 噪声使能
    else:
        noise_en=0

    noise_PSD=win.LE_AWGN_PSD.text()
    noise_PSD=float(noise_PSD)

    # if noise_PSD > 0:
    #     win.statusbar.showMessage('设置失败：AWGN功率谱密度过大', 3000)
    #     return -1

    std = -80.7918  # P = 2147352578(max) 时的功率密度，单位dBFS / Hz
    d_PSD = noise_PSD - std
    extra_P = 10 ** (d_PSD / 10)
    noise_P_linear = 2147483648 * extra_P
    noise_k= round( math.sqrt(noise_P_linear/132000) ) *4096

    Bytes = b''
    ID=11  #输出端衰减
    Bytes = Bytes + gen_subframe(ID, 2, 0, port_out, 0, output_k)
    ID = 10 # 输出端使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, port_out, 0, output_en) # 不在乎port_in和which_path
    ID = 8 # 噪声使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, port_out, 0, noise_en)
    ID = 9 # 噪声大小
    Bytes = Bytes + gen_subframe(ID, 2, 0, port_out, 0, noise_k)

    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

    #变化示意图的输出使能
    if output_en:
        widget0.LE_output_list[port_out].setEnabled(True)
    else:
        widget0.LE_output_list[port_out].setEnabled(False)

def send_f_sweep_restart():  ##扫频控制
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    port_in=win.comboBox_chan_input.currentIndex()
    ####################################################################
    port_out=win.comboBox_chan_output.currentIndex()
    ####################################################################
    which_path=win.comboBox_path.currentIndex()
    ####################################################################
    Bytes = b''
    ID=20  #扫频重启
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, 1)
    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_DDR_ctrl():   ## 输入时延
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    port_in=win.comboBox_input.currentIndex()

    DDR_delay=win.LE_DDR_delay.text()
    DDR_delay=int(DDR_delay)

    Bytes = b''
    ID=12  #DDR时延
    Bytes = Bytes + gen_subframe(ID, 4, port_in, 0, 0, DDR_delay)


    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_DDR_chn_num_ctrl():   ## 支持时延的输入
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    index0=win.comboBox_DDR_chn_num.currentIndex() + 1

    Bytes = b''
    ID=24  #支持时延的输入
    Bytes = Bytes + gen_subframe(ID, 1, 0, 0, 0, index0)

    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_RFin_connect_ctrl():  ## 输入拓扑控制
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    index0=win.comboBox_RFin_connect_ctrl.currentIndex()

    Bytes = b''
    ID=21  #输入拓扑控制
    Bytes = Bytes + gen_subframe(ID, 4, 0, 0, 0, index0)

    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_SS_ctrl(): ## 信号源相关控制
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    #
    if win.checkBox_SS_en.isChecked():
        SS_en=1
    else:
        SS_en=0
    #
    SS_freq=win.LE_SS_freq.text()
    SS_freq=float(SS_freq)
    SS_freq=round(SS_freq/SS_FREQ_UNIT)
    SS_freq=int(SS_freq)
    #
    if win.checkBox_SS_pulse_en.isChecked():
        SS_pulse_en=1
    else:
        SS_pulse_en=0
    #
    SS_pulse_width=win.LE_SS_pulse_width.text()
    SS_pulse_width=float(SS_pulse_width)
    SS_pulse_width=round(SS_pulse_width/CLK_TS)
    SS_pulse_width=int(SS_pulse_width)
    #
    SS_pulse_cycle=win.LE_SS_pulse_cycle.text()
    SS_pulse_cycle=float(SS_pulse_cycle)
    SS_pulse_cycle=round(SS_pulse_cycle/CLK_TS)
    SS_pulse_cycle=int(SS_pulse_cycle)
    #

    Bytes = b''
    ID=25  #信号源使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, 0, 0, SS_en)
    ID=26  #信号源频率
    Bytes = Bytes + gen_subframe(ID, 4, 0, 0, 0, SS_freq)
    ID=27  #信号源脉冲使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, 0, 0, SS_pulse_en)
    ID=28  #信号源脉冲脉宽
    Bytes = Bytes + gen_subframe(ID, 4, 0, 0, 0, SS_pulse_width)
    ID=29  #信号源脉冲周期
    Bytes = Bytes + gen_subframe(ID, 4, 0, 0, 0, SS_pulse_cycle)

    # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)

def make_send_uart(): ## 串口传输相关控制
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    uart_content=win.LE_uart.text()
    uart_content=uart_content.replace(' ','')   ##去掉空格
    chara_num=len(uart_content)
    if chara_num%2==1:#奇数个
        uart_content=uart_content[0:chara_num-1]  #去掉最后一个字符
        Bytes_num=int((chara_num-1)/2)
    else:             #偶数个
        Bytes_num = int(chara_num / 2)

    uart_Bytes=bytes.fromhex(uart_content)      ##string转为Bytes

        # uart_Bytes=b'\x7b\x3f\x38\x30'
        # nn=i%6 +48
        # uart_Bytes=uart_Bytes+ nn.to_bytes(1, byteorder='little')
        # uart_Bytes=uart_Bytes+b'\x35\x30\x30\x7d'
        #
    Bytes= b''
    Bytes = Bytes + b'\x1e'   # ID=30
    Bytes = Bytes + Bytes_num.to_bytes(1, byteorder='little')
    Bytes = Bytes + b'\x00'
    Bytes = Bytes + b'\x00'
    Bytes=Bytes+uart_Bytes
        # 加帧头加帧长加帧尾
    Bytes=Frame_forming(Bytes)
    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)


def send_fs_phase_rst():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    Bytes = b'\xfd\xb1\x85\x40\x05\x00\x21\x01\x00\x00\x01\xae\x86'  # ID=33

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已发送...', 3000)


def param_rst():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    Bytes=b'\xfd\xb1\x85\x40\x05\x00\x0d\x01\x00\x00\x01\xae\x86'

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已参数复位...', 3000)

    win.LE_channel_delay.setText('0')
    win.LE_delay.setText('0')
    win.LE_fs.setText('0')
    win.LE_atten.setText('0')
    win.LE_fs_start.setText('0')
    win.LE_fs_end.setText('0')
    win.LE_fs_speed.setText('0')
    #win.LE_Rayl_spread.setText('0')

    win.LE_DDR_delay.setText('0')

    win.LE_AWGN_PSD.setText('-100')
    #win.LE_output_atten.setText('0')

    win.checkBox_Rayl_en.setChecked(False)
    win.checkBox_path_en.setChecked(False)
    win.checkBox_AWGN_en.setChecked(False)
    win.checkBox_output_en.setChecked(False)

    win.LE_Rayl_spread.setEnabled(False)
    win.comboBox_Rayl_type.setEnabled(False)
    win.comboBox_fs_ctrl.setCurrentIndex(0)
    #win.comboBox_DDR_chn_num.setCurrentIndex(3)

    win.comboBox_RFin_connect_ctrl.setCurrentIndex(0)

    win.LE_phase_bias.setText('0')

    #示意图的相关清楚
    widget0.clear_all_lines()
    for i in range(8):
        widget0.LE_output_list[i].setEnabled(False)


def hardware_rst():
    if TCP_socket.TCP_connected==False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    Bytes=b'\xfd\xb1\x85\x40\x05\x00\x16\x01\x00\x00\x01\xae\x86'

    TCP_socket.my_socket.send(Bytes)
    win.statusbar.showMessage('已硬件复位...', 3000)

def Rayl_UI_switch():
    if win.checkBox_Rayl_en.isChecked():
        win.LE_Rayl_spread.setEnabled(True)
        win.comboBox_Rayl_type.setEnabled(True)
    else:
        win.LE_Rayl_spread.setEnabled(False)
        win.comboBox_Rayl_type.setEnabled(False)

# 全局变量存储导入的配置
imported_config = None

def import_json_config():
    """导入JSON配置文件"""
    global imported_config

    # 打开文件选择对话框
    file_path, _ = QFileDialog.getOpenFileName(
        win,
        "选择配置文件",
        "",
        "JSON Files (*.json);;All Files (*)"
    )

    if not file_path:
        return  # 用户取消

    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            imported_config = json.load(f)

        # 验证JSON格式
        if 'clusters' not in imported_config:
            win.statusbar.showMessage('配置文件格式错误：缺少clusters字段', 3000)
            win.label_config_status.setText('错误：格式不正确')
            imported_config = None
            return

        clusters = imported_config['clusters']
        num_clusters = len(clusters)

        # 打印读取的JSON数据
        print("=" * 60)
        print("【从JSON读取的数据】")
        print(f"文件路径: {file_path}")
        print(f"总cluster数量: {len(clusters)}")
        print("-" * 60)
        for i, cluster in enumerate(clusters[:min(num_clusters, 24)]):
            print(f"Cluster {i}: delay={cluster.get('delay', 'N/A')}s, power={cluster.get('power', 'N/A')}")
        print("=" * 60)

        # 检查是否超过24个多径
        if num_clusters > 24:
            win.statusbar.showMessage(f'警告：配置文件包含{num_clusters}个cluster，将只使用前24个', 3000)
            num_clusters = 24

        # 启用应用配置按钮
        win.pushButton_apply_config.setEnabled(True)
        win.label_config_status.setText(f'已导入配置：{num_clusters}个多径')
        win.statusbar.showMessage(f'成功导入配置：{num_clusters}个多径', 3000)

    except json.JSONDecodeError as e:
        win.statusbar.showMessage(f'JSON解析错误: {str(e)}', 3000)
        win.label_config_status.setText('错误：JSON格式错误')
        imported_config = None
    except Exception as e:
        win.statusbar.showMessage(f'导入失败: {str(e)}', 3000)
        win.label_config_status.setText(f'错误：{str(e)}')
        imported_config = None

def apply_json_config():
    """应用导入的JSON配置"""
    global imported_config

    # if imported_config is None:
    #     win.statusbar.showMessage('请先导入配置文件', 3000)
    #     return
    #
    # if TCP_socket.TCP_connected == False:
    #     win.statusbar.showMessage('设备未连接...', 3000)
    #     return -1

    # 获取当前选择的输入输出端口
    port_in = win.comboBox_chan_input.currentIndex()
    port_out = win.comboBox_chan_output.currentIndex()

    try:
        clusters = imported_config['clusters']
        num_clusters = min(len(clusters), 12)  # 最多12个cluster，将扩展为24条径

        # 构建参数帧
        Bytes = b''

        print("=" * 60)
        print("【应用配置 - 参数转换详情】")
        print(f"输入端口: {port_in}, 输出端口: {port_out}")
        print(f"配置cluster数量: {num_clusters} (将生成 {num_clusters * 2} 条多径)")
        print("-" * 60)

        subframe_list = []  # 用于保存子帧信息

        # ========== 前12条径：正常配置（瑞利衰落关闭） ==========
        print("【前12条径 - 瑞利衰落关闭】")
        for path_idx, cluster in enumerate(clusters[:num_clusters]):
            # 获取delay、power和xpr_db
            delay = cluster.get('delay', 0)  # 单位：秒
            power = cluster.get('power', 0)  # 归一化相对功率

            # 转换delay：从秒转换为时钟周期数 (CLK_TS = 5ns)
            path_delay = delay * 1e9  # 转换为ns
            path_delay = round(path_delay / CLK_TS)  # 转换为时钟周期数
            path_delay = int(path_delay)

            # 转换power：从归一化功率转换为k值
            if power > 0:
                # 将相对功率转换为dB
                atten_db = -10 * math.log10(power)
                # 转换为k值（参考make_send_path_ctrl中的公式）
                k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
                k = int(k)
            else:
                atten_db = 0
                k = 0  # 功率为0，完全衰减

            # 打印每条多径的转换结果
            print(f"多径{path_idx}: delay={delay}s -> {path_delay}周期, power={power} -> k={k} (衰减{atten_db:.2f}dB)")
            path_en = 1
            # 多径使能
            ID = 2
            subframe = gen_subframe(ID, 1, port_in, port_out, path_idx, path_en)
            Bytes = Bytes + subframe
            subframe_list.append(('使能', path_idx, subframe))

            # 多径时延
            ID = 3
            subframe = gen_subframe(ID, 2, port_in, port_out, path_idx, path_delay)
            Bytes = Bytes + subframe
            subframe_list.append(('时延', path_idx, subframe))

            # 多径幅值衰减
            ID = 7
            subframe = gen_subframe(ID, 2, port_in, port_out, path_idx, k)
            Bytes = Bytes + subframe
            subframe_list.append(('衰减', path_idx, subframe))

            # 多径频移设为0
            ID = 4
            subframe = gen_subframe(ID, 4, port_in, port_out, path_idx, 0)
            Bytes = Bytes + subframe
            subframe_list.append(('频移', path_idx, subframe))

            # 瑞利衰落使能设为0（前12条不启用）
            ID = 5
            subframe = gen_subframe(ID, 1, port_in, port_out, path_idx, 0)
            Bytes = Bytes + subframe
            subframe_list.append(('瑞利', path_idx, subframe))

        print("-" * 60)
        # ========== 后12条径：基于前12条，打开瑞利衰落，衰减加上xpr_db ==========
        print("【后12条径 - 瑞利衰落开启，衰减加上xpr_db】")
        for i, cluster in enumerate(clusters[:num_clusters]):
            path_idx = num_clusters + i  # 后12条径的索引：12-23

            # 获取delay、power和xpr_db
            delay = cluster.get('delay', 0)  # 单位：秒
            power = cluster.get('power', 0)  # 归一化相对功率
            xpr_db = cluster.get('xpr_db', 0)  # XPR值（dB）

            # 转换delay：从秒转换为时钟周期数 (CLK_TS = 5ns)
            path_delay = delay * 1e9  # 转换为ns
            path_delay = round(path_delay / CLK_TS)  # 转换为时钟周期数
            path_delay = int(path_delay)

            # 转换power：从归一化功率转换为k值，加上xpr_db
            if power > 0:
                # 将相对功率转换为dB
                atten_db = -10 * math.log10(power)
                # 加上xpr_db
                atten_db = atten_db + xpr_db
                # 转换为k值（参考make_send_path_ctrl中的公式）
                k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
                k = int(k)
            else:
                atten_db = xpr_db
                k = 0  # 功率为0，完全衰减

            # 打印每条多径的转换结果
            print(f"多径{path_idx}: delay={delay}s -> {path_delay}周期, power={power}, xpr_db={xpr_db}dB -> k={k} (总衰减{atten_db:.2f}dB)")
            path_en = 1
            # 多径使能
            ID = 2
            subframe = gen_subframe(ID, 1, port_in, port_out, path_idx, path_en)
            Bytes = Bytes + subframe
            subframe_list.append(('使能', path_idx, subframe))

            # 多径时延
            ID = 3
            subframe = gen_subframe(ID, 2, port_in, port_out, path_idx, path_delay)
            Bytes = Bytes + subframe
            subframe_list.append(('时延', path_idx, subframe))

            # 多径幅值衰减
            ID = 7
            subframe = gen_subframe(ID, 2, port_in, port_out, path_idx, k)
            Bytes = Bytes + subframe
            subframe_list.append(('衰减', path_idx, subframe))

            # 多径频移设为0
            ID = 4
            subframe = gen_subframe(ID, 4, port_in, port_out, path_idx, 0)
            Bytes = Bytes + subframe
            subframe_list.append(('频移', path_idx, subframe))

            # 瑞利衰落使能设为1（后12条启用）
            ID = 5
            subframe = gen_subframe(ID, 1, port_in, port_out, path_idx, 1)
            Bytes = Bytes + subframe
            subframe_list.append(('瑞利', path_idx, subframe))

        # 加帧头加帧长加帧尾
        Bytes = Frame_forming(Bytes)

        # 打印生成的完整帧数据
        print("-" * 60)
        print("【生成的完整帧数据】")
        print(f"帧总长度: {len(Bytes)} 字节")
        print(f"帧完整内容 (hex): {Bytes.hex()}")
        print("-" * 60)
        print("帧结构解析:")
        print(f"  帧头 (4字节): {Bytes[:4].hex()} (固定为 fd b1 85 40)")
        frame_len = int.from_bytes(Bytes[4:6], 'little')
        print(f"  帧长 (2字节): {Bytes[4:6].hex()} (小端值={frame_len}字节)")
        print(f"  数据部分 ({frame_len}字节): {Bytes[6:-2].hex()}")
        print(f"  帧尾 (2字节): {Bytes[-2:].hex()} (固定为 ae 86)")
        print("-" * 60)
        print("关键子帧详情 (前2个多径和后2个多径的使能、时延、衰减、频移、瑞利):")
        # 显示前2条径（索引0-1）的5个参数
        for name, path_idx, subframe in subframe_list[:10]:
            print(f"  多径{path_idx}-{name}: {subframe.hex()}")
            print(f"    └─ ID={subframe[0]:02x}, 字节数={subframe[1]}, 端口={subframe[2]:02x}, 路径={subframe[3]:02x}, 值={int.from_bytes(subframe[4:], 'little')}")
        print("  ...")
        # 显示后2条径（索引12-13）的5个参数（从列表中间开始）
        start_idx = num_clusters * 5  # 前12条径的参数数量
        for name, path_idx, subframe in subframe_list[start_idx:start_idx+10]:
            print(f"  多径{path_idx}-{name}: {subframe.hex()}")
            print(f"    └─ ID={subframe[0]:02x}, 字节数={subframe[1]}, 端口={subframe[2]:02x}, 路径={subframe[3]:02x}, 值={int.from_bytes(subframe[4:], 'little')}")
        print("=" * 60)

        # 发送
        TCP_socket.my_socket.send(Bytes)
        total_paths = num_clusters * 2  # 总共的多径数量
        win.statusbar.showMessage(f'已应用配置：{total_paths}条多径已发送（{num_clusters}个cluster扩展）', 3000)
        win.label_config_status.setText(f'已应用：{total_paths}条多径')

        # 更新示意图连线
        widget0.add_line([port_in, port_out])

    except Exception as e:
        win.statusbar.showMessage(f'应用配置失败: {str(e)}', 3000)
        win.label_config_status.setText(f'应用失败：{str(e)}')

def Rayl_UI_switch():
    if win.checkBox_Rayl_en.isChecked():
        win.LE_Rayl_spread.setEnabled(True)
        win.comboBox_Rayl_type.setEnabled(True)
    else:
        win.LE_Rayl_spread.setEnabled(False)
        win.comboBox_Rayl_type.setEnabled(False)

def fs_sweep_UI_switch():
    if win.comboBox_fs_ctrl.currentIndex()==0:
        win.LE_fs_start.setEnabled(False)
        win.LE_fs_end.setEnabled(False)
        win.LE_fs_speed.setEnabled(False)
    else:
        win.LE_fs_start.setEnabled(True)
        win.LE_fs_end.setEnabled(True)
        win.LE_fs_speed.setEnabled(True)

def clear_info_display():
    win.label_input_Lv.setText("--" )
    win.label_input_P.setText("--")
    win.label_output_Lv.setText("--")
    win.label_output_P.setText("--")
    win.label_output_P_with_noise.setText("--")

    win.label_input_Lv_2.setText("--" )
    win.label_input_P_2.setText("--")
    win.label_output_Lv_2.setText("--")
    win.label_output_P_2.setText("--")
    win.label_output_P_with_noise_2.setText("--")

    win.label_input_Lv_3.setText("--" )
    win.label_input_P_3.setText("--")
    win.label_output_Lv_3.setText("--")
    win.label_output_P_3.setText("--")
    win.label_output_P_with_noise_3.setText("--")

    win.label_input_Lv_4.setText("--" )
    win.label_input_P_4.setText("--")
    win.label_output_Lv_4.setText("--")
    win.label_output_P_4.setText("--")
    win.label_output_P_with_noise_4.setText("--")

    win.label_input_Lv_5.setText("--" )
    win.label_input_P_5.setText("--")
    win.label_output_Lv_5.setText("--")
    win.label_output_P_5.setText("--")
    win.label_output_P_with_noise_5.setText("--")

    win.label_input_Lv_6.setText("--" )
    win.label_input_P_6.setText("--")
    win.label_output_Lv_6.setText("--")
    win.label_output_P_6.setText("--")
    win.label_output_P_with_noise_6.setText("--")

    win.label_input_Lv_7.setText("--" )
    win.label_input_P_7.setText("--")
    win.label_output_Lv_7.setText("--")
    win.label_output_P_7.setText("--")
    win.label_output_P_with_noise_7.setText("--")

    win.label_input_Lv_8.setText("--" )
    win.label_input_P_8.setText("--")
    win.label_output_Lv_8.setText("--")
    win.label_output_P_8.setText("--")
    win.label_output_P_with_noise_8.setText("--")
def COPY_FRAME_upload_switch():
    if TCP_socket.TCP_connected == False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1

    if win.action_4.text() == '开启':
        send_data = b'\xfd\xb1\x85\x40\x05\x00\x0f\x01\x00\x00\x01\xae\x86'  # 打开复制帧回传
        TCP_socket.my_socket.send(send_data)
        win.action_4.setText('关闭')
    else:
        send_data = b'\xfd\xb1\x85\x40\x05\x00\x0f\x01\x00\x00\x00\xae\x86'  # 关闭复制帧回传
        TCP_socket.my_socket.send(send_data)
        win.action_4.setText('开启')

def INFO_FRAME_upload_switch():
    if TCP_socket.TCP_connected == False:
        win.statusbar.showMessage('设备未连接...', 3000)
        return -1
    
    if win.action_3.text()=='开启':
        send_data = b'\xfd\xb1\x85\x40\x05\x00\x0e\x01\x00\x00\x02\xae\x86'  # 打开设备信息帧发送
        TCP_socket.my_socket.send(send_data)
        win.action_3.setText('关闭')
    else:
        send_data = b'\xfd\xb1\x85\x40\x05\x00\x0e\x01\x00\x00\x00\xae\x86'  # 关闭设备信息帧发送
        TCP_socket.my_socket.send(send_data)
        clear_info_display()
        win.action_3.setText('开启')

class simulator_figure(QWidget,Ui_simulator_figure):
    resized = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resized.connect(self.ff)

        self.LE_input_list = [self.LE_input0, self.LE_input1, self.LE_input2, self.LE_input3, self.LE_input4, self.LE_input5, self.LE_input6, self.LE_input7]
        self.LE_output_list = [self.LE_output0, self.LE_output1, self.LE_output2, self.LE_output3, self.LE_output4, self.LE_output5, self.LE_output6, self.LE_output7]
        self.special_line=[0,0]
        #self.all_lines = [[1, 2], [3, 4], [7, 7]]
        self.all_lines=[]  #指示信道使能的所有线，包含很多list，每个list里有每个线的起点终点，比如[0,0]表示输入1-输出1的线

    def resizeEvent(self, event):       #界面大小改变的事件  #名字不能变
        self.resized.emit()

    def ff(self):
        print('界面大小改变')

    def get_Start_and_Desti(self,A,B):   #返回控件A的右中坐标和B的左中坐标

        A_geo = A.geometry()
        B_geo = B.geometry()
        A_right_center = [A_geo.x() + A_geo.width(),    A_geo.y() + int(A_geo.height() / 2)]
        B_left_center = [B_geo.x(),                     B_geo.y() + int(B_geo.height() / 2)]

        return A_right_center + B_left_center #list

    def paintEvent(self, event):        #画线  #名字不能变  #在比如位置改变时，重画
        painter = QPainter()
        painter.begin(self)
        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        painter.setPen(pen)

        #两两连线
        # for i in range(8):
        #     for j in range(8):
        #         pen = QPen(Qt.gray, 1, Qt.SolidLine)
        #         painter.setPen(pen)
        #         aa=self.get_Start_and_Desti(self.LE_input_list[i], self.LE_output_list[j])
        #         painter.drawLine(aa[0], aa[1], aa[2], aa[3])

        m, n = self.special_line[0], self.special_line[1]
        pen = QPen(Qt.lightGray, 3, Qt.SolidLine)
        painter.setPen(pen)
        aa = self.get_Start_and_Desti(self.LE_input_list[m], self.LE_output_list[n])
        painter.drawLine(aa[0], aa[1], aa[2], aa[3])

        if len(self.all_lines)==0:
            return
        for tt in self.all_lines:
            m, n = tt[0], tt[1]
            pen = QPen(Qt.black, 1, Qt.SolidLine)
            painter.setPen(pen)
            aa=self.get_Start_and_Desti(self.LE_input_list[m], self.LE_output_list[n])
            painter.drawLine(aa[0], aa[1], aa[2], aa[3])

    def add_line(self,list_in):  # list_in举例[1,2]
        if len(self.all_lines)==0:
            self.all_lines=[list_in, list_in]
            del self.all_lines[1]
        else:
            self.all_lines.append(list_in)

        self.update()

    def delete_line(self,list_in):  #如果list_in存在，将其删除
        if len(self.all_lines) == 0:
            print("线的list为空，无法删除！")
            return
        if list_in in self.all_lines:
            self.all_lines.remove(list_in)

        self.update()


    def clear_all_lines(self):
        self.all_lines=[]
        self.update()


    def change_special_line(self, list_in):
        self.special_line=list_in

        self.update()

def get_widget_right_center(A):   #返回控件的右中坐标

    A_geo = A.geometry()
    A_right_center = [A_geo.x() + A_geo.width(),    A_geo.y() + int(A_geo.height() / 2)]

    return A_right_center



def call_figure():
    aa = get_widget_right_center(win)  # 得到主界面的右中坐标
    widget0.move(aa[0], aa[1] - 200)  # 显示在主界面右边

    if not widget0.isVisible():
        widget0.show()



if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    frame_head = b'\xfd\xb1\x85\x40'  # 帧头
    frame_end = b'\xae\x86'


    TCP_socket=TCP_socket()
    win = MainForm()
    Thread_net_receive0 = Thread_net_receive()
    Thread_net_receive0.s_data_recv.connect(decode_Info_Frame_and_show)

    win.pushButton_ok_channel_delay.clicked.connect(make_send_channel_delay_ctrl)
    win.pushButton_ok.clicked.connect(make_send_path_ctrl)

    win.pushButton_ok_fs.clicked.connect(make_send_f_sweep_ctrl)
    win.pushButton_ok_DDR_set.clicked.connect(make_send_DDR_ctrl)
    win.pushButton_ok_2.clicked.connect(make_send_output_ctrl)
    win.pushButton_fs_restart.clicked.connect(send_f_sweep_restart)
    win.pushButton_ok_connect_ctrl.clicked.connect(make_send_RFin_connect_ctrl)
    win.pushButton_ok_DDR_chn_num.clicked.connect(make_send_DDR_chn_num_ctrl)
    win.pushButton_ok_SS_ctrl.clicked.connect(make_send_SS_ctrl)
    win.pushButton_ok_uart.clicked.connect(make_send_uart)
    win.pushButton_fs_phase_rst.clicked.connect(send_fs_phase_rst)

    # 连接导入和应用配置按钮
    win.pushButton_import_config.clicked.connect(import_json_config)
    win.pushButton_apply_config.clicked.connect(apply_json_config)

    win.action_param_rst.triggered.connect(param_rst)
    win.action_hardware_rst.triggered.connect(hardware_rst)

    win.checkBox_Rayl_en.clicked.connect(Rayl_UI_switch)
    win.comboBox_fs_ctrl.currentIndexChanged.connect(fs_sweep_UI_switch)

    win.action_3.triggered.connect(INFO_FRAME_upload_switch)
    win.action_4.triggered.connect(COPY_FRAME_upload_switch)

    #设初值
    win.comboBox_DDR_chn_num.setCurrentIndex(7)
    #win.checkBox_output_en.setEnabled(False)


    win.show()

    #示意图
    widget0=simulator_figure()

    # connect
    win.sig_change_special_line.connect(widget0.change_special_line) #改变信道输入输出下拉栏时，改变示意图连线
    win.action_5.triggered.connect(call_figure)


    #
    sys.exit(app.exec_())