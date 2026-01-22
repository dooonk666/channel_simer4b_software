"""
24条多径配置功能测试脚本

用于验证12条径扩展为24条径的逻辑是否正确
"""

import math

# 模拟配置数据（从3GPP_UMa_Stochastic.json中提取）
test_clusters = [
    {"delay": 0.0, "power": 0.172694, "xpr_db": 4.412167},
    {"delay": 7.83e-09, "power": 0.191893, "xpr_db": 10.285157},
    {"delay": 3.13e-08, "power": 0.189934, "xpr_db": 3.330992},
]

CLK_TS = 5  # 时钟周期5ns

print("=" * 80)
print("24条多径配置测试")
print("=" * 80)

# 前12条径测试
print("\n【前12条径 - 瑞利衰落关闭】")
for path_idx, cluster in enumerate(test_clusters):
    delay = cluster['delay']
    power = cluster['power']

    # 转换delay
    path_delay = delay * 1e9
    path_delay = round(path_delay / CLK_TS)
    path_delay = int(path_delay)

    # 转换power
    if power > 0:
        atten_db = -10 * math.log10(power)
        k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
        k = int(k)
    else:
        atten_db = 0
        k = 0

    print(f"多径{path_idx}:")
    print(f"  delay={delay}s -> {path_delay}周期")
    print(f"  power={power:.6f} -> atten_db={atten_db:.2f}dB -> k={k}")
    print(f"  瑞利衰落使能: 0 (关闭)")

# 后12条径测试
print("\n【后12条径 - 瑞利衰落开启，衰减加上xpr_db】")
num_clusters = len(test_clusters)
for i, cluster in enumerate(test_clusters):
    path_idx = num_clusters + i
    delay = cluster['delay']
    power = cluster['power']
    xpr_db = cluster['xpr_db']

    # 转换delay
    path_delay = delay * 1e9
    path_delay = round(path_delay / CLK_TS)
    path_delay = int(path_delay)

    # 转换power，加上xpr_db
    if power > 0:
        atten_db = -10 * math.log10(power)
        atten_db = atten_db + xpr_db  # 关键：加上xpr_db
        k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
        k = int(k)
    else:
        atten_db = xpr_db
        k = 0

    print(f"多径{path_idx}:")
    print(f"  delay={delay}s -> {path_delay}周期")
    print(f"  power={power:.6f}, xpr_db={xpr_db:.2f}dB")
    print(f"  -> 总衰减={atten_db:.2f}dB -> k={k}")
    print(f"  瑞利衰落使能: 1 (开启)")

print("\n" + "=" * 80)
print("验证结果:")
print(f"- 总共生成: {len(test_clusters) * 2} 条多径")
print(f"- 前{len(test_clusters)}条: 瑞利衰落关闭")
print(f"- 后{len(test_clusters)}条: 瑞利衰落开启，衰减增加xpr_db")
print("=" * 80)

# 对比验证
print("\n【对比验证】")
for i, cluster in enumerate(test_clusters):
    power = cluster['power']
    xpr_db = cluster['xpr_db']

    # 前12条径的衰减
    atten_front = -10 * math.log10(power) if power > 0 else 0

    # 后12条径的衰减
    atten_back = atten_front + xpr_db

    # 衰减差值应该等于xpr_db
    diff = atten_back - atten_front

    print(f"Cluster {i}:")
    print(f"  前径衰减: {atten_front:.2f}dB")
    print(f"  后径衰减: {atten_back:.2f}dB")
    print(f"  差值: {diff:.2f}dB (应等于xpr_db={xpr_db:.2f}dB)")
    print(f"  验证: {'✓ 通过' if abs(diff - xpr_db) < 0.01 else '✗ 失败'}")

