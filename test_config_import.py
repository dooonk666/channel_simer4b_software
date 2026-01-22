"""
测试配置导入和帧生成功能
"""
import json
import math

CLK_TS = 5  # 时钟周期 5ns

def gen_subframe(ID, Bytes_num, port_in, port_out, path, param_value):
    """生成参数子帧"""
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
    """加帧头加帧长加帧尾"""
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

def test_json_import():
    """测试JSON配置导入和帧生成"""

    # 读取JSON文件
    with open('3GPP_UMa_Stochastic.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    print("=" * 60)
    print("配置文件信息：")
    print(f"时间戳: {config['timestamp']}")
    print(f"路径损耗: {config['pathloss_db']} dB")
    print(f"是否LOS: {config['is_los']}")
    print(f"Clusters数量: {len(config['clusters'])}")
    print("=" * 60)

    # 模拟设置
    port_in = 0
    port_out = 0

    clusters = config['clusters']
    num_clusters = min(len(clusters), 24)  # 最多24个多径

    print(f"\n处理前 {num_clusters} 个clusters:")
    print("-" * 60)

    # 构建参数帧
    Bytes = b''

    # 遍历每个cluster
    for path_idx, cluster in enumerate(clusters[:num_clusters]):
        delay = cluster.get('delay', 0)  # 单位：秒
        power = cluster.get('power', 0)  # 归一化相对功率

        # 转换delay
        path_delay_ns = delay * 1e9  # 转换为ns
        path_delay = round(path_delay_ns / CLK_TS)  # 转换为时钟周期数
        path_delay = int(path_delay)

        # 转换power
        if power > 0:
            atten_db = -10 * math.log10(power)
            k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
            k = int(k)
        else:
            k = 0

        print(f"多径 {path_idx + 1}:")
        print(f"  delay: {delay:.6e} s = {path_delay_ns:.3f} ns = {path_delay} 时钟周期")
        print(f"  power: {power:.6f} = {atten_db:.3f} dB 衰减 => k = {k}")

        # 多径使能
        Bytes = Bytes + gen_subframe(2, 1, port_in, port_out, path_idx, 1)
        # 多径时延
        Bytes = Bytes + gen_subframe(3, 2, port_in, port_out, path_idx, path_delay)
        # 多径幅值衰减
        Bytes = Bytes + gen_subframe(7, 2, port_in, port_out, path_idx, k)
        # 分数时延
        Bytes = Bytes + gen_subframe(34, 1, port_in, port_out, path_idx, 0)
        # 多径频移
        Bytes = Bytes + gen_subframe(4, 4, port_in, port_out, path_idx, 0)
        # 相偏
        Bytes = Bytes + gen_subframe(32, 2, port_in, port_out, path_idx, 0)
        # 瑞利衰落使能
        Bytes = Bytes + gen_subframe(5, 1, port_in, port_out, path_idx, 0)

    # 禁用剩余多径
    for path_idx in range(num_clusters, 24):
        Bytes = Bytes + gen_subframe(2, 1, port_in, port_out, path_idx, 0)

    # 加帧头帧尾
    frame = Frame_forming(Bytes)

    print("-" * 60)
    print(f"\n生成的帧信息:")
    print(f"参数字节数: {len(Bytes)}")
    print(f"完整帧字节数: {len(frame)}")
    print(f"帧头: {frame[:4].hex()}")
    print(f"帧长度: {int.from_bytes(frame[4:6], 'little')}")
    print(f"帧尾: {frame[-2:].hex()}")
    print(f"\n完整帧 (前100字节): {frame[:100].hex()}")
    print("=" * 60)

if __name__ == "__main__":
    test_json_import()

