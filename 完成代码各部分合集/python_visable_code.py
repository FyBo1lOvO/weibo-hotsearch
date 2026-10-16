import pandas as pd
import os

def take_content_into_txt(file_path, output_path):
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 查看数据结构，确认是否有content列
    print("数据文件的列名：")
    print(df.columns.tolist())
    print("\n数据总行数：", len(df))
    print("\n前5行数据预览：")
    print(df.head())

    # 检查content列是否存在
    if 'content' in df.columns:
        print(f"\n成功找到'content'列，该列非空数据行数：{df['content'].notna().sum()}")
        print(f"'content'列空值数量：{df['content'].isna().sum()}")
    
        # 提取content列数据，去除空值
        content_data = df['content'].dropna()
    
        # 将数据保存到txt文件
        with open(output_path, 'w', encoding='utf-8') as f:
            for content in content_data:
                f.write(str(content) + '\n')
    
        print(f"\n数据已成功保存到：{output_path}")
        print(f"共保存了 {len(content_data)} 条非空的content数据")
    
        # 显示前3条保存的内容作为预览
        print("\n前3条content内容预览：")
        for i, content in enumerate(content_data.head(3)):
            print(f"{i+1}. {str(content)[:100]}..." if len(str(content)) > 100 else f"{i+1}. {str(content)}")
    else:
        print("\n错误：数据文件中没有找到'content'列")
        print("请检查列名是否正确，或确认数据文件是否正确")


def load_and_merge_data(entertainment_path, life_path, social_path, save_path=None): #合并三个细分板块的数据，输出为一个dataFrame对象
    """加载并合并所有数据"""
    print("正在加载数据...")
    
    # 加载数据
    entertainment_df = pd.read_csv(entertainment_path)
    life_df = pd.read_csv(life_path)
    social_df = pd.read_csv(social_path)
    
    # 为每个数据框添加来源标识
    entertainment_df['source'] = 'entertainment'
    life_df['source'] = 'life'
    social_df['source'] = 'social'
    
    # 统一列名以便合并
    entertainment_df['content'] = entertainment_df['热搜内容']
    life_df['content'] = life_df['热搜内容']
    social_df['content'] = social_df['清洗后内容']
    
    entertainment_df['heat'] = entertainment_df['热搜热度']
    life_df['heat'] = life_df['热搜热度']
    social_df['heat'] = social_df['热搜热度']
    
    # 合并数据
    combined_df = pd.concat([
        entertainment_df[['source', 'content', 'heat', '热搜排名']],
        life_df[['source', 'content', 'heat', '热搜排名']],
        social_df[['source', 'content', 'heat', '热搜排名']]
    ], ignore_index=True)
    
    # 保存数据到CSV文件
    if save_path:
        combined_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"合并数据已保存到 {save_path}")
    
    return combined_df, entertainment_df, life_df, social_df


import re
import jieba
import jieba.posseg as pseg
from nltk.corpus import stopwords
import nltk

# 下载nltk必要资源（首次运行需执行，后续可注释）
#nltk.download('stopwords')

def extract_keywords_from_txt(input_txt_path, output_file):
    """
    基于NLTK词库和中文分词，从TXT文件提取准确关键词
    :param input_txt_path: 输入TXT文件路径
    :param output_file: 输出TXT文件路径（可选）
    :return: 去重后的关键词列表
    """
    # 1. 读取外部TXT文件（兼容编码）
    try:
        with open(input_txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_txt_path, 'r', encoding='gbk') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误：未找到文件 {input_txt_path}")
        return []

    # 2. 文本预处理：移除特殊字符、多余空格
    content = re.sub(r'[\d\W]+', ' ', content)  # 删数字和特殊符号
    content = re.sub(r'\s+', ' ', content).strip()  # 合并多余空格

    # 3. 中文分词 + 词性筛选（优先保留名词、动词）
    # 定义需要保留的词性（n:名词, v:动词, a:形容词, ad:副词）
    target_pos = {'n', 'v', 'a', 'ad'}
    words_with_pos = pseg.cut(content)  # 带词性的分词结果
    
    # 筛选符合条件的词（长度≥2 + 目标词性）
    candidate_words = []
    for word, pos in words_with_pos:
        if len(word) >= 2 and pos in target_pos:
            candidate_words.append(word)

    # 4. 用NLTK停用词库过滤无意义词汇
    # 合并中英文停用词（NLTK默认含英文，补充常见中文停用词）
    stop_words = set(stopwords.words('english'))  # NLTK英文停用词
    chinese_stop_words = {'的', '是', '在', '和', '有', '我', '你', '他', '这', '那', '不', '也', '都'}
    all_stop_words = stop_words.union(chinese_stop_words)
    
    # 过滤停用词
    final_keywords = [word for word in candidate_words if word not in all_stop_words]

    # 5. 去重并保存结果
    unique_keywords = list(set(final_keywords))  # 去重
    if output_file and unique_keywords:
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(unique_keywords):  # 排序后保存，便于查看
                f.write(f"{word}\n")
        print(f"关键词已保存至：{output_file}")
        print(f"统计：原始分词{len(candidate_words)}个 → 过滤后{len(unique_keywords)}个关键词")

    return unique_keywords


# ------------------- 示例调用 -------------------
if __name__ == "__main__":
    # 输入文件：之前提取的content数据（可替换为你的文件路径）
    input_txt = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/content_extracted.txt"
    # 输出文件：准确关键词保存路径
    output_txt = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/accurate_keywords.txt"

    # 提取关键词
    keywords = extract_keywords_from_txt(input_txt, output_txt)
    
    # 预览前15个关键词
    if keywords:
        print("\n前15个关键词预览：")
        for i, word in enumerate(keywords[:15]):
            print(f"{i+1:2d}. {word}")


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
import os

# 定义颜色配置
colors = {
    'total': '#1f77b4',
    'entertainment': '#ff7f0e',
    'life': '#2ca02c',
    'social': '#d62728'
}

def analyze_topic_propagation(combined_csv_path, total_csv_path, entertainment_csv_path, 
                             life_csv_path, social_csv_path, save_path=None):
    """分析话题传播路径（从CSV文件读取数据）"""
    print("正在读取数据文件...")
    
    # 从CSV文件读取数据
    try:
        combined_df = pd.read_csv(combined_csv_path, encoding='utf-8-sig')
        total_df = pd.read_csv(total_csv_path, encoding='utf-8-sig')
        entertainment_df = pd.read_csv(entertainment_csv_path, encoding='utf-8-sig')
        life_df = pd.read_csv(life_csv_path, encoding='utf-8-sig')
        social_df = pd.read_csv(social_csv_path, encoding='utf-8-sig')
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        raise
    
    print("正在分析话题传播路径...")
    
    # 获取总榜前50热点
    top50_total = total_df.head(50)
    
    # 分析每个热点在其他板块的出现情况
    propagation_data = []
    
    for idx, row in top50_total.iterrows():
        content = row['热搜内容']
        total_heat = row['热搜热度']
        
        # 在其他板块中寻找相似内容
        entertainment_match = entertainment_df[entertainment_df['热搜内容'].str.contains(content[:6], na=False)]
        life_match = life_df[life_df['热搜内容'].str.contains(content[:6], na=False)]
        social_match = social_df[social_df['清洗后内容'].str.contains(content[:6], na=False)]
        
        propagation_info = {
            'content': content,
            'total_heat': total_heat,
            'entertainment_count': len(entertainment_match),
            'life_count': len(life_match),
            'social_count': len(social_match),
            'cross_board': len(entertainment_match) + len(life_match) + len(social_match) > 0
        }
        propagation_data.append(propagation_info)
    
    propagation_df = pd.DataFrame(propagation_data)
    
    # 保存数据到CSV文件
    if save_path:
        # 确保保存目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        propagation_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"传播分析数据已保存到 {save_path}")
    
    return propagation_df


def create_propagation_visualizations(propagation_df, save_img_path):
    """创建传播路径可视化（修复字体显示问题）"""
    print("正在创建可视化...")
    
    # ========== 核心修复：字体配置 ==========
    # 方案1：自动检测并设置可用中文字体（跨系统兼容）
    def set_chinese_font():
        # 常见中文字体列表（按优先级排序）
        font_names = [
            'SimHei',         # 黑体（Windows）
            'Microsoft YaHei',# 微软雅黑（Windows）
            'PingFang SC',    # 苹方（macOS）
            'Hiragino Sans GB',# 冬青黑体（macOS）
            'WenQuanYi Micro Hei', # 文泉驿微米黑（Linux）
            'DejaVu Sans',    # 备用无衬线字体
            'Arial Unicode MS'# 通用Unicode字体
        ]
        
        # 遍历字体列表，设置第一个可用的字体
        for font_name in font_names:
            try:
                plt.rcParams['font.sans-serif'] = [font_name]
                # 验证字体是否可用
                fm.FontProperties(family=font_name)
                print(f"成功设置字体: {font_name}")
                break
            except:
                continue
        
        # 解决负号显示问题
        plt.rcParams['axes.unicode_minus'] = False
        # 修复matplotlib 3.8+的字体缓存问题
        plt.rcParams['font.family'] = 'sans-serif'

    # 执行字体设置
    set_chinese_font()

    # ========== 绘图部分（保持逻辑不变） ==========
    # 1. 跨板块话题分布饼图
    cross_board_count = propagation_df['cross_board'].value_counts()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('热点话题传播路径分析', fontsize=20, fontweight='bold', y=0.95)
    
    # 饼图：跨板块分布
    colors_pie = [colors['total'], '#FFB6C1']
    ax1.pie(cross_board_count.values, labels=['仅总榜', '跨板块传播'], autopct='%1.1f%%', 
            colors=colors_pie, startangle=90, textprops={'fontsize': 12})  # 显式设置文字大小
    ax1.set_title('总榜前50话题跨板块传播分布', fontsize=14, fontweight='bold')
    
    # 堆叠条形图：各板块话题数量
    categories = ['娱乐', '生活', '社会']
    cross_board_data = propagation_df[propagation_df['cross_board'] == True]
    
    ent_count = cross_board_data['entertainment_count'].sum()
    life_count = cross_board_data['life_count'].sum()
    social_count = cross_board_data['social_count'].sum()
    
    category_counts = [ent_count, life_count, social_count]
    
    bars = ax2.bar(categories, category_counts, 
                   color=[colors['entertainment'], colors['life'], colors['social']])
    ax2.set_title('跨板块话题在各板块分布', fontsize=14, fontweight='bold')
    ax2.set_ylabel('话题数量', fontsize=12)
    ax2.tick_params(axis='x', labelsize=11)  # 设置坐标轴文字大小
    
    # 在柱状图上添加数值标签
    for bar, count in zip(bars, category_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(count)}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # 热力图：话题热度与跨板块传播关系
    heat_bins = pd.cut(propagation_df['total_heat'], bins=5)
    cross_board_by_heat = propagation_df.groupby([heat_bins, 'cross_board']).size().unstack(fill_value=0)
    
    sns.heatmap(cross_board_by_heat, annot=True, fmt='d', cmap='RdYlBu_r', 
                ax=ax3, cbar_kws={'label': '话题数量'}, annot_kws={'fontsize': 10})
    ax3.set_title('不同热度区间的话题传播情况', fontsize=14, fontweight='bold')
    ax3.set_xlabel('是否跨板块传播', fontsize=12)
    ax3.set_ylabel('热度区间', fontsize=12)
    ax3.tick_params(labelsize=10)
    
    # 散点图：热度vs跨板块传播程度
    cross_board_df = propagation_df[propagation_df['cross_board'] == True]
    if not cross_board_df.empty:
        total_cross_count = (cross_board_df['entertainment_count'] + 
                           cross_board_df['life_count'] + 
                           cross_board_df['social_count'])
        
        ax4.scatter(cross_board_df['total_heat'], total_cross_count, 
                   c=colors['total'], alpha=0.6, s=60)
        ax4.set_xlabel('总榜热度', fontsize=12)
        ax4.set_ylabel('跨板块出现次数', fontsize=12)
        ax4.set_title('话题热度与跨板块传播程度关系', fontsize=14, fontweight='bold')
        ax4.tick_params(labelsize=10)
        
        # 添加趋势线
        z = np.polyfit(cross_board_df['total_heat'], total_cross_count, 1)
        p = np.poly1d(z)
        ax4.plot(cross_board_df['total_heat'], p(cross_board_df['total_heat']), 
                "r--", alpha=0.8, linewidth=2)
    
    # 确保保存目录存在
    os.makedirs(os.path.dirname(save_img_path), exist_ok=True)
    
    # 保存图片（增加参数确保文字清晰）
    plt.tight_layout()
    plt.savefig(save_img_path, 
                dpi=300, 
                bbox_inches='tight', 
                facecolor='white',
                pad_inches=0.1)  # 增加内边距防止文字被裁剪
    plt.close()
    print(f"可视化图表已保存到: {save_img_path}")


# 使用示例
if __name__ == "__main__":
    # 替换为实际的CSV文件路径
    csv_paths = {
        'combined': 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/combined_data_test.csv',
        'total': 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/清洗后csv文件/cleaned_weibo_total_hotsearch_data.csv',
        'entertainment': 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/清洗后csv文件/cleaned_weibo_entertainment_hotsearch_data.csv',
        'life': 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/清洗后csv文件/cleaned_weibo_life_hotsearch_data.csv',
        'social': 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/清洗后csv文件/cleaned_weibo_social_hotsearch_data.csv'
    }

    # 分析话题传播
    propagation_result = analyze_topic_propagation(
        combined_csv_path=csv_paths['combined'],
        total_csv_path=csv_paths['total'],
        entertainment_csv_path=csv_paths['entertainment'],
        life_csv_path=csv_paths['life'],
        social_csv_path=csv_paths['social'],
        save_path='D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/propagation_analysis.csv'
    )
    
    # 创建可视化（修复字体后）
    create_propagation_visualizations(
        propagation_result,
        save_img_path='D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/hotspot_propagation_analysis.png'
    )


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 定义颜色配置（确保colors字典存在）
colors = {
    'entertainment': '#FF6B6B',
    'life': '#4ECDC4',
    'social': '#45B7D1',
    'total': '#96CEB4'
}

def analyze_user_engagement_patterns(csv_file_path, save_path, save_img_path):
    """
    分析用户参与度模式
    参数:
        csv_file_path: str, 输入CSV文件的路径
        save_path: str, 输出分析结果CSV文件的路径（可选）
    返回:
        source_analysis: 分组分析结果
    """
    print("正在读取数据文件...")
    # 从CSV文件读取数据
    combined_df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
    
    print("正在分析用户参与度模式...")
    
    # 按来源分组分析热度分布
    source_analysis = combined_df.groupby('source').agg({
        'heat': ['mean', 'median', 'std', 'count'],
        '热搜排名': 'mean'
    }).round(2)
    
    # 将多级索引转换为普通DataFrame以便保存
    source_analysis_df = pd.DataFrame(source_analysis.to_records())
    
    # 保存数据到CSV文件
    if save_path:
        source_analysis_df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"用户参与度分析数据已保存到 {save_path}")
    
    # 创建用户参与度可视化
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('用户参与度与话题热度分析', fontsize=20, fontweight='bold', y=0.95)
    
    # 热度分布箱线图
    heat_data = [combined_df[combined_df['source'] == source]['heat'].values 
                for source in ['entertainment', 'life', 'social', 'total']]
    labels = ['娱乐', '生活', '社会', '总榜']
    
    bp = ax1.boxplot(heat_data, labels=labels, patch_artist=True)
    colors_list = [colors['entertainment'], colors['life'], colors['social'], colors['total']]
    
    for patch, color in zip(bp['boxes'], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_title('各板块热度分布对比', fontsize=14, fontweight='bold')
    ax1.set_ylabel('热度值')
    ax1.set_yscale('log')
    
    # 排名vs热度散点图
    for source, color in zip(['entertainment', 'life', 'social', 'total'], colors_list):
        source_data = combined_df[combined_df['source'] == source]
        ax2.scatter(source_data['热搜排名'], source_data['heat'], 
                   c=color, label=source, alpha=0.6, s=30)
    
    ax2.set_xlabel('热搜排名')
    ax2.set_ylabel('热度值')
    ax2.set_title('排名与热度关系', fontsize=14, fontweight='bold')
    ax2.set_yscale('log')
    ax2.legend()
    
    # 热度区间分布
    heat_bins = [0, 100000, 500000, 1000000, float('inf')]
    heat_labels = ['低热度\n(<10万)', '中热度\n(10-50万)', '高热度\n(50-100万)', '超高热度\n(>100万)']
    
    for i, (source, color) in enumerate(zip(['entertainment', 'life', 'social', 'total'], colors_list)):
        source_data = combined_df[combined_df['source'] == source]
        heat_categories = pd.cut(source_data['heat'], bins=heat_bins, labels=heat_labels, right=False)
        heat_dist = heat_categories.value_counts()
        
        # 确保所有热度区间都有值（避免长度不一致）
        for label in heat_labels:
            if label not in heat_dist.index:
                heat_dist[label] = 0
        heat_dist = heat_dist.reindex(heat_labels)
        
        ax3.bar(np.arange(len(heat_labels)) + i*0.2, heat_dist.values, 
                width=0.2, label=source, color=color, alpha=0.8)
    
    ax3.set_xlabel('热度区间')
    ax3.set_ylabel('话题数量')
    ax3.set_title('各板块热度区间分布', fontsize=14, fontweight='bold')
    ax3.set_xticks(np.arange(len(heat_labels)) + 0.3)
    ax3.set_xticklabels(heat_labels)
    ax3.legend()
    
    # 平均热度对比
    avg_heat_by_source = combined_df.groupby('source')['heat'].mean().sort_values(ascending=True)
    # 确保顺序正确
    source_order = ['entertainment', 'life', 'social', 'total']
    avg_heat_by_source = avg_heat_by_source.reindex(source_order, fill_value=0)
    
    # 获取对应的颜色
    bar_colors = [colors[source] for source in avg_heat_by_source.index]
    bars = ax4.barh(range(len(avg_heat_by_source)), avg_heat_by_source.values, 
                    color=bar_colors)
    
    # 创建标签映射
    source_label_map = {
        'entertainment': '娱乐',
        'life': '生活',
        'social': '社会',
        'total': '总榜'
    }
    ax4.set_yticks(range(len(avg_heat_by_source)))
    ax4.set_yticklabels([source_label_map[source] for source in avg_heat_by_source.index])
    ax4.set_xlabel('平均热度')
    ax4.set_title('各板块平均热度对比', fontsize=14, fontweight='bold')
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, avg_heat_by_source.values)):
        ax4.text(value + value*0.01 if value > 0 else 1, bar.get_y() + bar.get_height()/2,
                f'{int(value):,}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_img_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("用户参与度分析完成！")
    print(f"可视化图表已保存到: ",save_img_path)
    
    return source_analysis

# 使用示例
if __name__ == "__main__":
    # 调用函数示例
    # 输入CSV文件路径
    input_csv_path = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/combined_data_test.csv"
    # 输出分析结果路径（可选）
    output_csv_path = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/user_engagement_analysis.csv"
    output_img_path = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/user_engagement_analysis.png"
    
    # 执行分析
    analysis_result = analyze_user_engagement_patterns(
        csv_file_path=input_csv_path,
        save_path=output_csv_path,
        save_img_path=output_img_path
    )
    
    # 打印分析结果
    print("\n用户参与度分析结果:")
    print(analysis_result)


import pandas as pd
import os

def generate_insights_report(propagation_csv_path, source_analysis_csv_path, output_path="insights_report.csv"):
    """
    参数:
    propagation_csv_path: str - 传播数据CSV文件路径
    source_analysis_csv_path: str - 来源分析数据CSV文件路径
    output_path: str - 分析结果CSV文件输出路径
    """
    print("正在读取数据文件...")
    
    # 读取外部CSV文件
    try:
        # 读取传播数据
        propagation_df = pd.read_csv(propagation_csv_path, encoding='utf-8-sig')
        print(f"✅ 成功读取传播数据: {propagation_csv_path} (共{len(propagation_df)}行)")
        
        # 读取来源分析数据（用户数据格式：source列作为板块名称，非索引）
        source_analysis = pd.read_csv(source_analysis_csv_path, encoding='utf-8-sig')
        print(f"✅ 成功读取来源分析数据: {source_analysis_csv_path} (共{len(source_analysis)}行)")
        
    except FileNotFoundError as e:
        print(f"❌ 错误：找不到文件 - {e}")
        return []
    except Exception as e:
        print(f"❌ 读取CSV文件时出错: {e}")
        return []
    
    print("正在生成洞察报告...")
    
    insights = []
    # 存储分析数据的字典
    analysis_data = {}
    
    # 1. 跨板块传播分析
    # 检查必要的列是否存在
    required_cols = ['cross_board', 'total_heat', 'entertainment_count', 'life_count', 'social_count']
    missing_cols = [col for col in required_cols if col not in propagation_df.columns]
    
    if missing_cols:
        print(f"⚠️ 警告：传播数据缺少必要列 - {missing_cols}")
        insights.append(f"⚠️ 数据不完整：缺少列 {missing_cols}，部分分析无法完成")
    else:
        # 确保cross_board列是布尔类型
        propagation_df['cross_board'] = propagation_df['cross_board'].astype(bool)
        
        cross_board_rate = (propagation_df['cross_board'].sum() / len(propagation_df)) * 100
        insights.append(f"📊 跨板块传播率：总榜前50话题中，{cross_board_rate:.1f}%的话题在其他板块也有出现，显示热点话题具有较强的跨领域影响力。")
        # 保存到分析数据
        analysis_data['跨板块传播率(%)'] = round(cross_board_rate, 1)
        analysis_data['总话题数'] = len(propagation_df)
        analysis_data['跨板块话题数'] = propagation_df['cross_board'].sum()
        
        # 2. 各板块传播分布
        cross_board_data = propagation_df[propagation_df['cross_board'] == True]
        if not cross_board_data.empty:
            ent_prop = cross_board_data['entertainment_count'].sum()
            life_prop = cross_board_data['life_count'].sum()
            social_prop = cross_board_data['social_count'].sum()
            total_prop = ent_prop + life_prop + social_prop
            
            ent_pct = ent_prop/total_prop*100 if total_prop > 0 else 0
            life_pct = life_prop/total_prop*100 if total_prop > 0 else 0
            social_pct = social_prop/total_prop*100 if total_prop > 0 else 0
            
            insights.append(f"🔄 传播分布：跨板块话题中，娱乐板块出现{ent_prop}次({ent_pct:.1f}%)，生活板块{life_prop}次({life_pct:.1f}%)，社会板块{social_prop}次({social_pct:.1f}%)")
            
            # 保存到分析数据
            analysis_data['娱乐板块传播次数'] = ent_prop
            analysis_data['娱乐板块传播占比(%)'] = round(ent_pct, 1)
            analysis_data['生活板块传播次数'] = life_prop
            analysis_data['生活板块传播占比(%)'] = round(life_pct, 1)
            analysis_data['社会板块传播次数'] = social_prop
            analysis_data['社会板块传播占比(%)'] = round(social_pct, 1)
        
        # 3. 热度与传播关系
        high_heat_total = len(propagation_df[propagation_df['total_heat'] > 500000])
        high_heat_cross = propagation_df[(propagation_df['cross_board'] == True) & 
                                       (propagation_df['total_heat'] > 500000)]
        high_heat_cross_count = len(high_heat_cross)
        
        if high_heat_total > 0:
            high_heat_cross_pct = high_heat_cross_count / high_heat_total * 100
            insights.append(f"🔥 高热度传播：在热度超过50万的话题中，{high_heat_cross_count}个话题实现了跨板块传播，占高热度话题的{high_heat_cross_pct:.1f}%")
            
            # 保存到分析数据
            analysis_data['高热度话题总数(>50万)'] = high_heat_total
            analysis_data['跨板块传播的高热度话题数'] = high_heat_cross_count
            analysis_data['高热度话题跨板块传播占比(%)'] = round(high_heat_cross_pct, 1)
        else:
            insights.append(f"🔥 高热度传播：暂无热度超过50万的话题")
            analysis_data['高热度话题总数(>50万)'] = 0
            analysis_data['跨板块传播的高热度话题数'] = 0
            analysis_data['高热度话题跨板块传播占比(%)'] = 0.0
    
    # 4. 用户参与度洞察 - 修复部分：适配用户数据格式
    source_metrics = []
    
    # 检查用户数据的关键列是否存在（适配用户实际数据格式）
    required_source_cols = ['source', "('heat', 'mean')", "('heat', 'count')"]
    missing_source_cols = [col for col in required_source_cols if col not in source_analysis.columns]
    
    if missing_source_cols:
        insights.append(f"⚠️ 来源分析数据格式不正确，缺少必要列：{missing_source_cols}")
        print(f"⚠️ 警告：来源分析数据缺少必要的列 - {missing_source_cols}")
    else:
        # 提取各板块的热度和话题数量信息（用户数据格式：source列为板块名称）
        for _, row in source_analysis.iterrows():
            source_name = row['source']
            avg_heat = row["('heat', 'mean')"]
            topic_count = row["('heat', 'count')"]
            
            # 处理空值
            avg_heat = avg_heat if pd.notna(avg_heat) else 0
            topic_count = topic_count if pd.notna(topic_count) else 0
            
            # 美化板块名称显示
            source_display = {
                'entertainment': '娱乐',
                'life': '生活',
                'social': '社会'
            }.get(source_name.lower(), source_name.capitalize())
            
            insights.append(f"📈 {source_display}板块：平均热度{avg_heat:,.0f}，话题数量{int(topic_count)}个")
            
            # 收集板块数据用于CSV保存
            source_metrics.append({
                '板块名称': source_display,
                '板块原始标识': source_name,
                '平均热度': round(avg_heat, 0),
                '话题数量': int(topic_count),
                '平均热搜排名': round(row["('热搜排名', 'mean')"], 1) if "('热搜排名', 'mean')" in source_analysis.columns else 0
            })
        
        # 将板块数据添加到分析数据中，便于汇总查看
        for metric in source_metrics:
            prefix = metric['板块名称']
            analysis_data[f'{prefix}板块_平均热度'] = metric['平均热度']
            analysis_data[f'{prefix}板块_话题数量'] = metric['话题数量']
            if '平均热搜排名' in metric:
                analysis_data[f'{prefix}板块_平均热搜排名'] = metric['平均热搜排名']
    
    # 创建综合分析数据的DataFrame并保存
    try:
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 1. 保存主分析数据（跨板块传播等汇总信息）
        main_df = pd.DataFrame([analysis_data])
        main_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # 2. 如果有板块详细数据，保存到单独的文件
        if source_metrics:
            source_output_path = os.path.splitext(output_path)[0] + "_板块详情.csv"
            source_df = pd.DataFrame(source_metrics)
            source_df.to_csv(source_output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 板块详细分析数据已保存至: {source_output_path}")
        
        print(f"✅ 洞察报告分析数据已保存至: {output_path}")
        
    except Exception as e:
        print(f"❌ 保存CSV文件时出错: {e}")
    
    return insights

# 测试修改后的代码（使用用户上传的文件）
if __name__ == "__main__":
    # 配置文件路径（适配/mnt目录）
    # 注意：需要用户提供propagation_analysis.csv文件，这里先使用模拟数据测试用户数据部分
    import numpy as np
    
    # 1. 生成模拟的传播数据（用于测试完整流程）
    sample_propagation_data = {
        'cross_board': np.random.choice([True, False], 50, p=[0.9, 0.1]),  # 90%跨板块传播率
        'total_heat': np.random.randint(100000, 1000000, 50),
        'entertainment_count': np.random.randint(0, 3, 50),
        'life_count': np.random.randint(0, 2, 50),
        'social_count': np.random.randint(0, 5, 50)
    }
    propagation_df = pd.DataFrame(sample_propagation_data)
    propagation_csv_path = 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/propagation_analysis.csv'
    propagation_df.to_csv(propagation_csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 已生成模拟传播数据: {propagation_csv_path}")
    
    # 2. 使用用户上传的来源分析数据
    source_analysis_csv_path = 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/user_engagement_analysis.csv'
    
    # 3. 输出路径
    output_csv_path = 'D:/Jupyter Code/数据采集期末论文/2025.12.03.2118微博数据/可视化数据/insights_report.csv'
    
    # 4. 执行洞察报告生成
    print("\n开始执行洞察报告生成...")
    report_insights = generate_insights_report(propagation_csv_path, source_analysis_csv_path, output_csv_path)
    
    # 5. 打印最终报告
    print("\n" + "="*60)
    print("📋 完整洞察报告")
    print("="*60)
    for i, insight in enumerate(report_insights, 1):
        print(f"{i:2d}. {insight}")
    
    # 6. 显示生成的文件列表
    print(f"\n" + "="*60)
    print("📁 生成的文件列表")
    print("="*60)
    generated_files = [
        propagation_csv_path,
        source_analysis_csv_path,
        output_csv_path,
        os.path.splitext(output_csv_path)[0] + "_板块详情.csv"
    ]
    for file_path in generated_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024  # 转换为KB
            print(f"✅ {os.path.basename(file_path)} - 大小: {file_size:.1f}KB")
