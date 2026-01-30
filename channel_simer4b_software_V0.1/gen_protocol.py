import socket
import time

#产生参数子帧
def gen_subframe(ID, Bytes_num, port_in, port_out, path, param_value):
    Bytes= b''
    Bytes = Bytes + ID.to_bytes(1, byteorder='little')
    Bytes = Bytes + Bytes_num.to_bytes(1, byteorder='little')
    Bytes = Bytes + (port_in * 16 + port_out).to_bytes(1, byteorder='little')
    Bytes = Bytes + path.to_bytes(1, byteorder='little')



    if (Bytes_num == 1 or 2 or 4):
        Bytes = Bytes + param_value.to_bytes(Bytes_num, byteorder='little', signed=True)

    else:
        print('Bytes_num unexpect!')

    return Bytes


####################################################################
##                            参数                                 ##
####################################################################

frame_type=2  # 1:多径控制   2:输出端相关参数控制

frame_head = b'\xfd\xb1\x85\x40' #帧头
frame_end=b'\xae\x86'

if frame_type==1:
    port_in = 0 # 0~7
    port_out = 1 # 0~7
    output_en = 1 # 输出使能
    which_path = 3 # 0~3

    path_en = 1 #多径使能
    path_delay = 3000 #  #单位25 / 3ns
    f_start = 000000 * 35.791    # 单位1 / 35.791

    f_end = 1000000 * 35.791 # 单位1 / 35.791
    f_sweep_v = 0.999 * pow(2,15) # 单位1/35.791/2^15Hz / us
    f_sweep_ctrl = 0  #0定频 # 1扫频（到终点停止） # 2扫频（到终点折返） # 3暂停
    f_sweep_restart = 0

    k = 10000 # 0~32768 # 单位1 / 32768

    Rayl_en = 0 # 瑞利衰落使能
    type = 'su'
    bandwidth = 0.1


    f_start = round(f_start)
    f_end = round(f_end)
    f_sweep_v = round(f_sweep_v)

elif frame_type==2:
    port_out = 0 # 0~7
    output_en = 1 # 输出使能
    noise_en = 0 # 噪声使能
    noise_PSD = -47 # 噪声功率谱密度 单位dBm / MHz
    # noise_k = 30000 # 0~65535 # 控制噪声电平   1 / 4096
    output_atten = 0 # 输出端衰减 #0: power/1  #1:power/4  #2: power/16  #3:power/64  #4: power/256.......


    std = -47.51 # k = 30000 时的功率密度，单位dBm / MHz
    d_PSD = noise_PSD - std
    extra_k = 10 ** (d_PSD / 10 / 2)
    noise_k = round(30000 * extra_k)


#bbb=gen_subframe(1,1,0,0,0,3)



####################################################################
##                           生成帧的字节流
####################################################################
Bytes=b''
if frame_type==1:
    ID = 10 # 输出端使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, port_out, 0, output_en) # 不在乎port_in和which_path
    ID = 2 # 多径使能
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, path_en)
    ID = 3 # 多径时延
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, path_delay)
    ID = 4 # 多径频移
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, f_start)
    ID = 7 # 多径幅值衰减
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, k)

    ID = 17 # 扫频终点
    Bytes = Bytes + gen_subframe(ID, 4, port_in, port_out, which_path, f_end)
    ID = 18 # 扫频速度
    Bytes = Bytes + gen_subframe(ID, 2, port_in, port_out, which_path, f_sweep_v)
    ID = 19 # 扫频控制
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, f_sweep_ctrl)
    ID = 20 # 扫频重载
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, f_sweep_restart)

    ID = 5 # 多径瑞利衰落使能
    Bytes = Bytes + gen_subframe(ID, 1, port_in, port_out, which_path, Rayl_en)

elif frame_type==2:
    ID = 10 # 输出端使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, port_out, 0, output_en) # 不在乎port_in和which_path
    ID = 8 # 噪声使能
    Bytes = Bytes + gen_subframe(ID, 1, 0, port_out, 0, noise_en)
    ID = 9 # 噪声大小
    Bytes = Bytes + gen_subframe(ID, 2, 0, port_out, 0, noise_k)
    ID = 11 # 输出端增益
    Bytes = Bytes + gen_subframe(ID, 2, 0, port_out, 0, output_atten)



#加帧长
frame_Bytes_num=len(Bytes)
aaa=frame_Bytes_num.to_bytes(2, byteorder='little')
Bytes=aaa + Bytes

#加帧头
Bytes=frame_head + Bytes
#加帧尾
Bytes=Bytes + frame_end




#  创建客户端
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#  连接
#  soc.connect(('192.168.43.141', 8087))
soc.connect(('192.168.1.10', 7))
send_data = Bytes

soc.send(send_data)

time.sleep(1)

recv_data=soc.recv(1024)
print(recv_data)



soc.close()