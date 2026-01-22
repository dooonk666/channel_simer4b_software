"""
演示帧结构的示例脚本
"""
import math

CLK_TS = 5  # 时钟周期 5ns

def gen_subframe(ID, Bytes_num, port_in, port_out, path, param_value):
    """生成子帧"""
    Bytes = b''
    Bytes = Bytes + ID.to_bytes(1, byteorder='little')
    Bytes = Bytes + Bytes_num.to_bytes(1, byteorder='little')
    Bytes = Bytes + (port_in * 16 + port_out).to_bytes(1, byteorder='little')
    Bytes = Bytes + path.to_bytes(1, byteorder='little')

    if param_value > 0:
        Bytes = Bytes + param_value.to_bytes(Bytes_num, byteorder='little', signed=False)
    else:
        Bytes = Bytes + param_value.to_bytes(Bytes_num, byteorder='little', signed=True)

    return Bytes

def Frame_forming(Bytes):
    """添加帧头、帧长、帧尾"""
    frame_head = b'\xfd\xb1\x85\x40'
    frame_end = b'\xae\x86'

    # 加帧长
    frame_Bytes_num = len(Bytes)
    aaa = frame_Bytes_num.to_bytes(2, byteorder='little')
    Bytes = aaa + Bytes
    # 加帧头
    Bytes = frame_head + Bytes
    # 加帧尾
    Bytes = Bytes + frame_end

    return Bytes

# 示例：配置2条多径
print("=" * 80)
print("帧结构演示 - 配置2条多径")
print("=" * 80)

port_in = 0
port_out = 0

# 模拟JSON数据
clusters = [
    {'delay': 0.000000100, 'power': 1.0},      # 多径0: 100ns延迟, 全功率
    {'delay': 0.000000500, 'power': 0.5},      # 多径1: 500ns延迟, 一半功率
]

print("\n【1. JSON 原始数据】")
for i, cluster in enumerate(clusters):
    print(f"Cluster {i}: delay={cluster['delay']}s, power={cluster['power']}")

print("\n【2. 参数转换】")
Bytes = b''
subframe_list = []

for path_idx, cluster in enumerate(clusters):
    delay = cluster['delay']
    power = cluster['power']

    # 转换delay
    path_delay = int(round(delay * 1e9 / CLK_TS))

    # 转换power
    if power > 0:
        atten_db = -10 * math.log10(power)
        k = int(round(10 ** (-atten_db / 10 / 2) * (2 ** 15)))
    else:
        k = 0

    print(f"\n多径{path_idx}:")
    print(f"  delay: {delay}s = {delay*1e9}ns -> {path_delay} 时钟周期")
    print(f"  power: {power} -> 衰减 {atten_db:.2f}dB -> k={k}")

    # 生成子帧
    # 使能
    sf = gen_subframe(2, 1, port_in, port_out, path_idx, 1)
    Bytes += sf
    subframe_list.append(('使能', path_idx, sf))

    # 时延
    sf = gen_subframe(3, 2, port_in, port_out, path_idx, path_delay)
    Bytes += sf
    subframe_list.append(('时延', path_idx, sf))

    # 衰减
    sf = gen_subframe(7, 2, port_in, port_out, path_idx, k)
    Bytes += sf
    subframe_list.append(('衰减', path_idx, sf))

print("\n【3. 子帧详细结构】")
print("子帧格式: [ID][字节数][端口][路径][参数值]")
print("-" * 80)
for name, path_idx, subframe in subframe_list:
    ID = subframe[0]
    bytes_num = subframe[1]
    port = subframe[2]
    path = subframe[3]
    value = int.from_bytes(subframe[4:], 'little')

    print(f"多径{path_idx}-{name:4s}: {subframe.hex():20s} 长度={len(subframe)}字节")
    print(f"  └─ ID={ID:3d}(0x{ID:02x}), 字节数={bytes_num}, 端口=0x{port:02x}, 路径={path}, 值={value}")

print("\n【4. 完整帧结构】")
Bytes = Frame_forming(Bytes)
print(f"帧总长度: {len(Bytes)} 字节")
print(f"完整帧 (hex): {Bytes.hex()}")
print("-" * 80)
print("帧结构分解:")
print(f"  [帧头 4字节]  : {Bytes[:4].hex():20s} (固定: fd b1 85 40)")
frame_len = int.from_bytes(Bytes[4:6], 'little')
print(f"  [帧长 2字节]  : {Bytes[4:6].hex():20s} (小端值={frame_len})")
print(f"  [数据 {frame_len}字节]: {Bytes[6:6+frame_len].hex()}")
print(f"  [帧尾 2字节]  : {Bytes[-2:].hex():20s} (固定: ae 86)")

print("\n【5. 数据部分子帧列表】")
data_part = Bytes[6:-2]
offset = 0
idx = 0
print(f"{'索引':<6} {'偏移':<8} {'ID':<6} {'字节数':<8} {'端口':<6} {'路径':<6} {'值':<12} {'十六进制'}")
print("-" * 80)
while offset < len(data_part):
    ID = data_part[offset]
    bytes_num = data_part[offset + 1]
    port = data_part[offset + 2]
    path = data_part[offset + 3]

    subframe_len = 4 + bytes_num
    value = int.from_bytes(data_part[offset+4:offset+subframe_len], 'little') if bytes_num > 0 else 0

    subframe_hex = data_part[offset:offset+subframe_len].hex()
    print(f"{idx:<6} {offset:<8} {ID:<6} {bytes_num:<8} 0x{port:02x}   {path:<6} {value:<12} {subframe_hex}")

    offset += subframe_len
    idx += 1

print("=" * 80)

