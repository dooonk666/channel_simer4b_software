"""
配置导入功能演示脚本
展示如何��序化地使用配置导入功能
"""
import json
import math

def demonstrate_config_processing():
    """演示配置处理流程"""

    print("=" * 70)
    print("配置导入功能演示")
    print("=" * 70)

    # 1. 读取JSON配置
    print("\n【步骤1】读取JSON配置文件")
    print("-" * 70)

    with open('3GPP_UMa_Stochastic.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    print(f"✓ JSON文件读取成功")
    print(f"  - 时间戳: {config['timestamp']}")
    print(f"  - 路径损耗: {config['pathloss_db']:.2f} dB")
    print(f"  - LOS/NLOS: {'LOS' if config['is_los'] else 'NLOS'}")
    print(f"  - Clusters数量: {len(config['clusters'])}")

    # 2. 验证配置
    print("\n【步骤2】验证配置格式")
    print("-" * 70)

    if 'clusters' not in config:
        print("✗ 错误：缺少clusters字段")
        return False

    clusters = config['clusters']
    num_clusters = len(clusters)

    print(f"✓ 配置格式正确")

    if num_clusters > 24:
        print(f"⚠ 警告：配置包含{num_clusters}个cluster，将只使用前24个")
        num_clusters = 24
    else:
        print(f"✓ Clusters数量在支持范围内（{num_clusters}/24）")

    # 3. 参数转换演示
    print("\n【步骤3】参数转换演示")
    print("-" * 70)
    print(f"{'多径':<6} {'Delay(s)':<12} {'Delay(ns)':<10} {'周期':<6} {'Power':<10} {'衰减(dB)':<10} {'k值':<8}")
    print("-" * 70)

    CLK_TS = 5  # 时钟周期5ns

    for i, cluster in enumerate(clusters[:min(5, num_clusters)]):  # 只显示前5个
        delay = cluster.get('delay', 0)
        power = cluster.get('power', 0)

        # 转换delay
        delay_ns = delay * 1e9
        delay_cycles = round(delay_ns / CLK_TS)

        # 转换power
        if power > 0:
            atten_db = -10 * math.log10(power)
            k = round(10 ** (-atten_db / 10 / 2) * (2 ** 15))
        else:
            atten_db = float('inf')
            k = 0

        print(f"{i+1:<6} {delay:<12.2e} {delay_ns:<10.2f} {delay_cycles:<6} {power:<10.6f} {atten_db:<10.2f} {k:<8}")

    if num_clusters > 5:
        print(f"... (还有{num_clusters-5}个clusters)")

    # 4. 帧结构说明
    print("\n【步骤4】生成的帧结构")
    print("-" * 70)

    params_per_path = 7  # 每个多径7个参数子帧
    subframe_size_avg = 8  # 平均每个子帧8字节
    total_paths = 24  # 总共24个多径

    # 计算帧大小
    active_paths_bytes = num_clusters * params_per_path * subframe_size_avg
    inactive_paths_bytes = (total_paths - num_clusters) * 1 * subframe_size_avg
    total_params_bytes = active_paths_bytes + inactive_paths_bytes
    total_frame_bytes = total_params_bytes + 8  # 加上帧头(4) + 帧长(2) + 帧尾(2)

    print(f"活动多径参数: {num_clusters} × 7个子帧 × ~8字节 = ~{active_paths_bytes}字节")
    print(f"禁用多径参数: {total_paths-num_clusters} × 1个子帧 × ~8字节 = ~{inactive_paths_bytes}字节")
    print(f"总参数字节: ~{total_params_bytes}字节")
    print(f"完整帧字节: ~{total_frame_bytes}字节 (含帧头帧尾)")
    print(f"帧长度限制: 4000字节 (当前使用{total_frame_bytes/4000*100:.1f}%)")

    # 5. 发送的参数明细
    print("\n【步骤5】每个多径发送的参数")
    print("-" * 70)

    param_list = [
        ("ID=2",  "多径使能",         "1字节", "1 (启用)"),
        ("ID=3",  "多径时延",         "2字节", "从delay转换"),
        ("ID=7",  "多径幅值衰减",     "2字节", "从power转换"),
        ("ID=34", "分数时延",         "1字节", "0 (默认)"),
        ("ID=4",  "多径频移",         "4字节", "0 (默认)"),
        ("ID=32", "相偏",            "2字节", "0 (默认)"),
        ("ID=5",  "瑞利衰落使能",     "1字节", "0 (默认)"),
    ]

    for param_id, param_name, param_size, param_value in param_list:
        print(f"  {param_id:<8} {param_name:<15} {param_size:<8} = {param_value}")

    # 6. 使用建议
    print("\n【步骤6】使用建议")
    print("-" * 70)
    print("1. 确保设备已通过TCP连接")
    print("2. 选择正确的输入输出端口")
    print("3. 导入JSON配置文件")
    print("4. 检查状态标签确认导入成功")
    print("5. 点击应用配置按钮")
    print("6. 观察状态栏确认发送成功")

    # 7. 常见场景
    print("\n【步骤7】常见应用场景")
    print("-" * 70)
    print("场景1: 3GPP标准信道模型测试")
    print("  - 导入UMa/UMi/InH等标准场景配置")
    print("  - 快速切换不同测试场景")
    print("")
    print("场景2: 自定义多径配置")
    print("  - 使用JSON文件定义特殊的多径结构")
    print("  - 精确控制每个多径的delay和power")
    print("")
    print("场景3: 批量测试")
    print("  - 准备多个配置文件")
    print("  - 逐个导入测试")
    print("  - 记录测试结果")

    # 8. 性能指标
    print("\n【步骤8】性能指标")
    print("-" * 70)
    print(f"支持的多径数: 24")
    print(f"导入速度: <1秒")
    print(f"帧生成时间: <1秒")
    print(f"内存占用: 最小")
    print(f"网络传输: 取决于连接质量")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)

    return True

def create_sample_json():
    """创建一个示例JSON配置文件"""

    print("\n【额外功能】创建示例JSON配置")
    print("-" * 70)

    sample_config = {
        "timestamp": "2026-01-20T12:00:00",
        "pathloss_db": 80.0,
        "is_los": True,
        "clusters": [
            {
                "delay": 0.0,
                "power": 0.5,
                "aoa_phi": 0.0,
                "note": "主径"
            },
            {
                "delay": 1e-7,
                "power": 0.3,
                "aoa_phi": 10.0,
                "note": "第二径"
            },
            {
                "delay": 2e-7,
                "power": 0.2,
                "aoa_phi": -10.0,
                "note": "第三径"
            }
        ]
    }

    filename = "sample_config.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=4, ensure_ascii=False)

    print(f"✓ 示例配置已创建: {filename}")
    print(f"  - 包含3个clusters")
    print(f"  - 可用于快速测试")

    return filename

if __name__ == "__main__":
    # 运行主演示
    success = demonstrate_config_processing()

    if success:
        print("\n")
        # 创建示例配置
        sample_file = create_sample_json()
        print(f"\n提示：可以使用 {sample_file} 进行快速测试")

