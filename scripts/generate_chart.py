import re
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import defaultdict
import os
import numpy as np

# 定义 CCF-A 类会议
CCF_A_VENUES = [
    'CVPR', 'ICCV', 'ECCV', 'NeurIPS', 'ICML', 'AAAI', 'IJCAI',
    'TPAMI', 'IJCV', 'TIP', 'TIFS'
]


def parse_readme(filepath):
    """解析 README.md 文件，统计每年论文总数和 CCF-A 论文数"""
    year_counts = defaultdict(int)
    ccf_a_counts = defaultdict(int)
    year_pattern = re.compile(r'\b(20[123]\d)\b')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_paper_section = False
        for line in lines:
            if "## 📝 Papers & Methods" in line or "## 🌟 Spotlight" in line:
                in_paper_section = True
            if "## 💾 Datasets" in line:
                in_paper_section = False

            if not in_paper_section:
                continue

            if '[' in line and ']' in line and ('http' in line or 'arXiv' in line):
                year_match = year_pattern.search(line)
                if year_match:
                    year = int(year_match.group(1))
                    year_counts[year] += 1
                    is_ccf_a = False
                    for venue in CCF_A_VENUES:
                        if re.search(r'\b' + re.escape(venue) + r'\b', line, re.IGNORECASE):
                            is_ccf_a = True
                            break
                    if is_ccf_a:
                        ccf_a_counts[year] += 1
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None, None
    return year_counts, ccf_a_counts


def plot_chart_pami(year_counts, ccf_a_counts, output_path):
    """
    绘制符合 IEEE/PAMI 风格的出版级图表
    """
    if not year_counts:
        print("No data found to plot.")
        return

    # 数据准备
    years = sorted(year_counts.keys())
    total_vals = [year_counts[y] for y in years]
    ccf_a_vals = [ccf_a_counts[y] for y in years]

    # --- 样式设置 ---
    # 尝试使用衬线字体 (接近 Times New Roman)
    plt.rcParams['font.family'] = 'serif'
    # 如果系统有 Times New Roman，可以显式指定:
    # plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['font.size'] = 11
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['axes.linewidth'] = 1.0  # 坐标轴线宽

    # 设置画布大小 (宽, 高) 英寸
    # 8x5 适合 Github 展示，论文中单栏图通常宽 3.5 英寸
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # --- 绘图 ---
    bar_width = 0.35
    index = np.arange(len(years))

    # 配色：使用专业的深蓝和砖红，对比鲜明且不刺眼
    # zorder=3 确保柱状图在网格线之上
    # edgecolors='black' 添加黑色边框，增强界限感

    # Total Publications 柱状图
    rects1 = ax.bar(index, total_vals, bar_width,
                    label='Total Publications',
                    color='#4A90E2', alpha=0.9,
                    edgecolor='black', linewidth=0.8, zorder=3)

    # CCF-A 柱状图：添加 hatch='//' 纹理，黑白打印也可识别
    rects2 = ax.bar(index + bar_width, ccf_a_vals, bar_width,
                    label='CCF-A Venues',
                    color='#E74C3C', alpha=0.9,
                    edgecolor='black', linewidth=0.8, hatch='//', zorder=3)

    # --- 细节修饰 ---

    # 网格线：仅保留 Y 轴，虚线，灰色，置于底层
    ax.yaxis.grid(True, linestyle='--', which='major', color='#D3D3D3', alpha=0.5, zorder=0)
    ax.set_axisbelow(True)  # 确保网格线在图形后面

    # 坐标轴标签
    ax.set_xlabel('Year', fontweight='bold', labelpad=8)
    ax.set_ylabel('Number of Papers', fontweight='bold', labelpad=8)

    # 标题 (可选，论文中通常不需要图标题，但在 Github README 中很好用)
    ax.set_title('Publication Trend Analysis', fontweight='bold', pad=15)

    # X轴刻度
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(years)

    # 移除顶部和右侧边框 (Tufte 风格 / 现代学术风格)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 加粗左侧和底部边框
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['bottom'].set_linewidth(1.0)

    # 图例：去框，置于左上角
    ax.legend(frameon=False, loc='upper left')

    # 数值标签函数
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f'{height}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

    autolabel(rects1)
    autolabel(rects2)

    # 紧凑布局
    plt.tight_layout()

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 保存：SVG 适合网页和矢量编辑，PDF 适合 LaTeX 插入
    # 同时保存 png 以防万一
    plt.savefig(output_path, format='svg', bbox_inches='tight')
    # plt.savefig(output_path.replace('.svg', '.png'), format='png', dpi=300, bbox_inches='tight')

    print(f"Chart saved to {output_path}")
    plt.close()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 如果脚本在 scripts/ 下，往上两级可能才是根目录，请根据实际情况调整
    # 假设结构是 root/scripts/plot.py -> root/README.md
    project_root = os.path.dirname(base_dir)

    readme_path = os.path.join(project_root, 'README.md')
    output_image_path = os.path.join(project_root, 'assets', 'publication_trend.svg')

    print(f"Reading from: {readme_path}")
    # 运行解析
    y_counts, a_counts = parse_readme(readme_path)

    if y_counts:
        print("Parsed data successfully.")
        plot_chart_pami(y_counts, a_counts, output_image_path)
    else:
        print("No data parsed or file not found. Generating demo chart...")
        # 演示用假数据
        demo_y = {2020: 30, 2021: 45, 2022: 60, 2023: 85}
        demo_a = {2020: 10, 2021: 15, 2022: 25, 2023: 40}
        plot_chart_pami(demo_y, demo_a, output_image_path)