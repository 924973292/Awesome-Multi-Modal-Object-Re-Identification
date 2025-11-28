import re
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# 定义 CCF-A 类会议（根据需要添加或修改，这里包含了CV领域主要的A类和部分ReID常投的顶会）
CCF_A_VENUES = [
    'CVPR', 'ICCV', 'ECCV', 'NeurIPS', 'ICML', 'AAAI', 'IJCAI',
    'TPAMI', 'IJCV', 'TIP'  # 期刊也加入
]


def parse_readme(filepath):
    """解析 README.md 文件，统计每年论文总数和 CCF-A 论文数"""
    year_counts = defaultdict(int)
    ccf_a_counts = defaultdict(int)

    # 正则表达式匹配年份 (例如: 2023, 2024, 2025)
    year_pattern = re.compile(r'\b(20[123]\d)\b')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_paper_section = False
        for line in lines:
            # 简单判断是否在论文列表区域（根据实际README结构调整）
            if "## 📝 Papers & Methods" in line or "## 🌟 Spotlight" in line:
                in_paper_section = True
            if "## 💾 Datasets" in line:
                in_paper_section = False

            if not in_paper_section:
                continue

            # 寻找包含链接的行，通常这代表一篇论文条目
            if '[' in line and ']' in line and ('http' in line or 'arXiv' in line):
                # 查找年份
                year_match = year_pattern.search(line)
                if year_match:
                    year = int(year_match.group(1))
                    year_counts[year] += 1

                    # 查找是否为 CCF-A
                    is_ccf_a = False
                    for venue in CCF_A_VENUES:
                        # 使用边界匹配符 \b 确保精确匹配 (例如避免匹配到 WACV 中的 CV)
                        if re.search(r'\b' + re.escape(venue) + r'\b', line, re.IGNORECASE):
                            is_ccf_a = True
                            break
                    if is_ccf_a:
                        ccf_a_counts[year] += 1

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None, None

    return year_counts, ccf_a_counts


def plot_chart(year_counts, ccf_a_counts, output_path):
    """绘制柱状图并保存为 SVG"""
    if not year_counts:
        print("No data found to plot.")
        return

    years = sorted(year_counts.keys())
    total_vals = [year_counts[y] for y in years]
    ccf_a_vals = [ccf_a_counts[y] for y in years]

    # 设置绘图风格
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制柱状图
    bar_width = 0.35
    index = range(len(years))

    bars1 = ax.bar(index, total_vals, bar_width, label='Total Publications', color='#4a90e2', alpha=0.8)
    # CCF-A 的柱子稍微错开一点，或者叠加显示
    bars2 = ax.bar([i + bar_width for i in index], ccf_a_vals, bar_width, label='CCF-A Venues (Estimated)',
                   color='#e74c3c', alpha=0.9)

    # 添加数值标签
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 垂直偏移 3 个点
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

    add_labels(bars1)
    add_labels(bars2)

    # 设置图表元素
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Papers', fontsize=12, fontweight='bold')
    ax.set_title('Multi-Modal Object Re-ID Publication Trends in This Repository', fontsize=14, fontweight='bold',
                 pad=20)
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(years, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # 移除顶部和右侧边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 确保 assets 目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存为矢量 SVG，清晰度高
    plt.savefig(output_path, format='svg', bbox_inches='tight')
    print(f"Chart saved to {output_path}")
    plt.close()


if __name__ == "__main__":
    # 假定脚本在 scripts/ 目录下运行，README 在上一级目录
    # Changed: Removed one os.path.dirname() call
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 去掉base_dir的最后一层目录
    base_dir = os.path.dirname(base_dir)
    print(f"Base directory: {base_dir}")
    readme_path = os.path.join(base_dir, 'README.md')
    output_image_path = os.path.join(base_dir, 'assets', 'publication_trend.svg')

    print(f"Reading from: {readme_path}")
    y_counts, a_counts = parse_readme(readme_path)

    if y_counts:
        print("Parsed data:")
        print(f"Total: {dict(y_counts)}")
        print(f"CCF-A: {dict(a_counts)}")
        plot_chart(y_counts, a_counts, output_image_path)