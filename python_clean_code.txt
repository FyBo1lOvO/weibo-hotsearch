import pandas as pd
import numpy as np
import ast
import re
from collections import Counter


def clean_entertainment_hotsearch(input_path, output_path):
    # 读取原始数据
    df = pd.read_csv(input_path)
    
    #娱乐分类细化映射（基于补充的娱乐细分关键词）
    entertainment_category_mapping = {
        '艺人': '艺人动态',
        '电影': '影视娱乐',
        '综艺': '综艺娱乐',
        '游戏,网红': '跨界娱乐',
        '剧集': '影视娱乐',
        '演出': '现场娱乐',
        '作品衍生': '娱乐周边',
        '艺人,体育': '跨界娱乐',
        # 补充娱乐细分场景
        '音乐': '音乐娱乐',
        '动漫': '动漫娱乐',
        '电竞': '电竞娱乐',
        '直播': '直播娱乐',
        '短视频': '短视频娱乐'
    }
    
    # 1. 多分类处理 - 拆分为主分类和子分类，并应用分类细化映射
    def split_category(category):
        if pd.isna(category):
            return '未分类', None, '未分类'
        
        category_str = str(category).strip()
        # 先拆分主副分类
        if ',' in category_str:
            main_cat_raw, sub_cat = category_str.split(',', 1)
            main_cat_raw = main_cat_raw.strip()
            sub_cat = sub_cat.strip()
        else:
            main_cat_raw = category_str.strip()
            sub_cat = None
        
        # 应用细化分类映射
        refined_main_cat = entertainment_category_mapping.get(main_cat_raw, main_cat_raw)
        return main_cat_raw, sub_cat, refined_main_cat  # 返回原始主分类、子分类、细化主分类
    
    # "细化主分类"字段，用于更精准的分类统计
    df[['原始主分类', '子分类', '细化主分类']] = df['热搜分类'].apply(
        lambda x: pd.Series(split_category(x))
    )
    
    # 艺人相关关键词（用于辅助识别艺人信息关联性）
    artist_related_keywords = [
        '工作室', '经纪公司', '粉丝', '应援', '后援会',
        '专辑', '单曲', 'MV', '演唱会', '巡演',
        '拍戏', '杀青', '开机', '路透', '定妆照',
        '代言', '广告', '活动', '红毯', '颁奖礼',
        '绯闻', '恋爱', '结婚', '离婚', '生子'
    ]
    
    # 2. 艺人字段标准化 + 艺人关联性判断
    def standardize_artists(artist_str):
        try:
            if pd.isna(artist_str) or artist_str.strip() == '{}':
                return []
            # 解析字符串为列表并清理空格
            artists = ast.literal_eval(artist_str)
            if isinstance(artists, list):
                return [artist.strip() for artist in artists if artist.strip()]
            elif isinstance(artists, str):
                return [artists.strip()] if artists.strip() else []
            else:
                return []
        except:
            return []
    
    df['标准化艺人列表'] = df['相关艺人'].apply(standardize_artists)
    df['艺人数量'] = df['标准化艺人列表'].apply(len)
    df['是否有艺人信息'] = df['艺人数量'] > 0
    
    # 基于关键词判断内容与艺人的关联性（即使艺人字段为空，也能识别艺人相关内容）
    def judge_artist_relevance(content):
        content = str(content).lower()
        return any(keyword in content for keyword in artist_related_keywords)
    
    df['是否艺人相关内容'] = df['热搜内容'].apply(judge_artist_relevance)
    
    # 3. 内容长度计算
    df['内容长度'] = df['热搜内容'].apply(lambda x: len(str(x).strip()))
    
    # 4. 数据类型统一
    df['热搜排名'] = df['热搜排名'].astype(int)
    df['热搜热度'] = df['热搜热度'].astype(int)  # 完全保留原始热度
    df['数据清洗时间'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 最终字段（细化分类、艺人关联性字段）
    final_columns = [
        '热搜排名', '原始主分类', '细化主分类', '子分类',  # 包含原始与细化分类，兼顾兼容性与精准性
        '热搜内容', '内容长度', '是否艺人相关内容',  # 新增艺人关联性判断
        '热搜热度', '标准化艺人列表', '艺人数量', '是否有艺人信息', 
        '数据清洗时间'
    ]
    
    # 保存结果
    df[final_columns].to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 娱乐热搜数据清洗完成")
    print(f"📁 输出路径: {output_path}")
    print(f"📊 细化分类分布: {df['细化主分类'].value_counts().to_dict()}")
    print(f"👥 含艺人信息记录数: {df['是否有艺人信息'].sum()}/{len(df)}")
    print(f"🔗 艺人相关内容数: {df['是否艺人相关内容'].sum()}/{len(df)}")
    
    return df[final_columns]


def clean_life_hotsearch_final(input_path, output_path):
    # 读取原始数据
    df = pd.read_csv(input_path)
    
    # 1. 分类体系标准化
    category_mapping = {
        '情感': '情感生活',
        '幽默': '休闲娱乐',
        '健康医疗': '健康养生',
        '民生新闻': '生活服务',
        '科学科普': '知识科普',
        '数码': '数码科技',
        '美食': '美食烹饪'
    }
    
    def process_life_category(category):
        if pd.isna(category):
            return '未分类', '未分类', False
        
        category_str = str(category).strip()
        is_multi = ',' in category_str
        
        if is_multi:
            main_cat, sub_cat = category_str.split(',', 1)
            main_cat = category_mapping.get(main_cat.strip(), main_cat.strip())
            sub_cat = category_mapping.get(sub_cat.strip(), sub_cat.strip())
            return main_cat, sub_cat, True
        else:
            main_cat = category_mapping.get(category_str, category_str)
            return main_cat, None, False
    
    df[['主分类', '子分类', '是否多分类']] = df['热搜分类'].apply(
        lambda x: pd.Series(process_life_category(x))
    )
    
    # 2. 生活领域关键词提取
    # 丰富的生活领域关键词（重点拓展科技数码企业/IP）
    life_keywords = {
        '健康': ['健康', '医疗', '疾病', '养生', '医院', '医生',
            '感冒', '发烧', '咳嗽', '过敏', '高血压', '糖尿病', '癌症',
            '体检', '疫苗', '吃药', '输液', '手术', '康复',
            '睡眠', '作息', '饮食', '营养', '维生素', '蛋白质',
            '运动', '健身', '减肥', '塑形', '瑜伽', '跑步'],
        '美食': ['吃', '美食', '烹饪', '餐厅', '菜谱', '食材',
            '火锅', '烧烤', '奶茶', '咖啡', '蛋糕', '面包',
            '中餐', '西餐', '日料', '韩餐', '泰餐', '意餐',
            '家常菜', '快手菜', '甜品', '零食', '饮料', '酒水',
            '做饭', '炒菜', '煲汤', '烘焙', '凉拌', '煎烤'],
        '数码': ['手机', '电脑', '数码', '科技', '互联网', 'APP',
            # 科技企业/产品IP
            '苹果', '华为', '小米', 'OPPO', 'vivo', '荣耀', '三星',
            'iPhone', 'iPad', 'Mac', '华为Mate', '华为P系列', '小米14',
            'AirPods', 'Apple Watch', '智能手表', '手环', '耳机',
            '笔记本', '平板', '相机', '无人机', '智能家居', '路由器',
            '微软', '谷歌', '亚马逊', '特斯拉', '比亚迪', '蔚来',
            '微信', '支付宝', '抖音', '快手', '淘宝', '京东'],
        '情感': ['爱情', '婚姻', '家庭', '情感', '恋爱', '分手',
            '情侣', '夫妻', '父母', '子女', '亲情', '友情',
            '孤独', '开心', '难过', '焦虑', '抑郁', '幸福',
            '约会', '求婚', '婚礼', '离婚', '复婚', '异地恋',
            '婆媳', '翁婿', '妯娌', '闺蜜', '兄弟'],
        '生活': ['生活', '日常', '居家', '家居', '装修', '家电',
            '租房', '买房', '搬家', '收纳', '清洁', '整理',
            '家电', '冰箱', '空调', '洗衣机', '电视', '烤箱',
            '快递', '外卖', '网购', '超市', '商场', '菜市场',
            '旅行', '旅游', '酒店', '机票', '景点', '攻略']
}
    
    def extract_life_keywords(content):
        content = str(content).lower()
        matched = []
        for keyword_type, keywords in life_keywords.items():
            if any(keyword in content for keyword in keywords):
                matched.append(keyword_type)
        return matched if matched else ['其他']
    
    df['内容关键词'] = df['热搜内容'].apply(extract_life_keywords)
    df['关键词数量'] = df['内容关键词'].apply(len)
    
    # 3. 内容长度计算（保留，用于特征分析）
    df['内容长度'] = df['热搜内容'].apply(lambda x: len(str(x).strip()))
    
    # 4. 数据时间标记
    df['数据清洗时间'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 最终字段（删除是否短内容字段）
    final_columns = [
        '热搜排名', '主分类', '子分类', '是否多分类', '热搜内容', 
        '内容长度', '内容关键词', '关键词数量', '热搜热度', '数据清洗时间'
    ]
    
    # 保存结果
    df[final_columns].to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 生活热搜数据清洗完成")
    print(f"📁 输出路径: {output_path}")
    print(f"📊 分类分布: {df['主分类'].value_counts().to_dict()}")
    print(f"🔑 关键词分布: {df['内容关键词'].apply(lambda x: x[0]).value_counts().to_dict()}")
    
    return df[final_columns]


def clean_social_hotsearch_final(input_path, output_path):

    # 读取原始数据
    df = pd.read_csv(input_path)
    
    # 1. 分类处理与标准化
# 丰富后的社会分类层级（新增社会细分场景映射）
    social_category_hierarchy = {
        # 基础分类映射
        '民生新闻': '社会民生',
        '国内时政': '政治',
        '国际时政': '国际',
        '海外新闻': '国际',
        '财经': '经济',
        '数码': '科技',
        '健康医疗': '健康',
        '舆论监督': '社会监督',
        '互联网': '科技',
        #社会细分场景分类
        '疫情防控': '社会民生',
        '教育政策': '社会民生',
        '就业创业': '社会民生',
        '环境保护': '社会民生',
        '交通安全': '社会民生',
        '食品安全': '社会民生',
        '社会治安': '社会民生',
        '社会保障': '社会民生',
        '房产政策': '经济',
        '金融市场': '经济',
        '国际贸易': '经济',
        '科技创新': '科技',
        '数字经济': '科技',
        '文化产业': '文化',
        '体育赛事': '体育'
}

    # 若有社会内容关键词提取逻辑，可补充以下细分关键词
    social_subject_keywords = {
        '国际事务': ['中国', '美国', '日本', '韩国', '俄罗斯', '英国', '法国',
                '德国', '印度', '巴西', '联合国', '北约', '欧盟', 'G20',
                '外交', '签证', '护照', '留学', '移民', '贸易', '合作'],
        '国内民生': ['疫情', '疫苗', '核酸', '防控', '教育', '医疗', '就业',
                '社保', '医保', '养老', '住房', '交通', '食品安全', '环境'],
        '经济金融': ['股票', '基金', '债券', '汇率', '利率', '通胀', '通缩',
                    'GDP', 'CPI', 'PPI', '企业', '公司', '破产', '上市', '融资'],
        '科技数码': ['5G', 'AI', '人工智能', '大数据', '云计算', '区块链',
                '元宇宙', '芯片', '半导体', '软件', '硬件', '互联网', 'APP']
    }
    def process_social_category(category):
        if pd.isna(category):
            return '未分类', [], False
        
        category_str = str(category).strip()
        categories = [cat.strip() for cat in category_str.split(',')]
        standardized_cats = [social_category_hierarchy.get(cat, cat) for cat in categories]
        
        return standardized_cats[0], standardized_cats[1:], len(categories) > 1
    
    df[['主分类', '次要分类', '是否多分类']] = df['热搜分类'].apply(
        lambda x: pd.Series(process_social_category(x))
    )
    
    # 2. 数值信息提取（规范格式）
    def extract_numeric_info(content):
        content = str(content)
        numeric_info = {}
        
        # 提取百分比
        percent_pattern = r'(\d+\.?\d*)%'
        percent_matches = re.findall(percent_pattern, content)
        if percent_matches:
            numeric_info['百分比'] = [float(match) for match in percent_matches]
        
        # 提取金额（统一为万元）
        money_pattern = r'(\d+\.?\d*)\s*(万|亿)元'
        money_matches = re.findall(money_pattern, content)
        if money_matches:
            money_info = []
            for amount, unit in money_matches:
                amount_num = float(amount)
                if unit == '亿':
                    amount_num *= 10000
                money_info.append(amount_num)
            numeric_info['金额_万元'] = money_info
        
        return numeric_info if numeric_info else None
    
    df['数值信息'] = df['热搜内容'].apply(extract_numeric_info)
    df['是否包含数值'] = df['数值信息'].notna()
    
    # 3. 敏感事件标记
    sensitive_keywords = [
        '恶性案件', '死亡', '事故', '灾难', '暴力', '犯罪', 
        '冲突', '抗议', '维权', '自杀', '杀人'
    ]
    
    def mark_sensitive_content(content):
        content = str(content).lower()
        for keyword in sensitive_keywords:
            if keyword in content:
                return True, keyword
        return False, None
    
    df[['是否敏感内容', '敏感关键词']] = df['热搜内容'].apply(
        lambda x: pd.Series(mark_sensitive_content(x))
    )
    
    # 4. 特殊字符清理
    def clean_special_chars(content):
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？；：""''（）【】、·…—-]', '', str(content))
        return cleaned.strip()
    
    df['清洗后内容'] = df['热搜内容'].apply(clean_special_chars)
    
    # 5. 内容长度计算
    df['内容长度'] = df['清洗后内容'].apply(len)
    
    # 6. 数据时间标记
    df['数据清洗时间'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 最终字段
    final_columns = [
        '热搜排名', '主分类', '次要分类', '是否多分类', '清洗后内容',
        '内容长度', '是否包含数值', '数值信息', '是否敏感内容', '敏感关键词',
        '热搜热度', '数据清洗时间'
    ]
    
    # 保存结果
    df[final_columns].to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 社会热搜数据清洗完成")
    print(f"📁 输出路径: {output_path}")
    print(f"⚠️  敏感内容记录数: {df['是否敏感内容'].sum()}")
    print(f"🔢 含数值信息记录数: {df['是否包含数值'].sum()}")
    
    return df[final_columns]



def clean_total_hotsearch_final(input_path, output_path):

    # 读取原始数据
    df = pd.read_csv(input_path)
    
    # 1. 基于内容补充分类信息
    # 丰富后的领域关键词字典（重点拓展社会细分和生活科技企业IP）
    domain_keywords = {
    '娱乐': ['艺人', '电影', '综艺', '剧集', '演出', 'CP', '明星', '歌手', 
            '演唱会', '专辑', '电视剧', '网剧', '真人秀', '选秀', '红毯',
            '颁奖礼', '票房', '收视率', '粉丝', '应援', '绯闻', '离婚', '结婚'],
    '社会': ['案件', '新闻', '事件', '民生', '时政', '财经', '国际',
            # 国家/地区名称
            '中国', '美国', '日本', '韩国', '俄罗斯', '英国', '法国', '德国',
            '印度', '巴西', '澳大利亚', '加拿大', '意大利', '西班牙', '朝鲜',
            '韩国', '越南', '泰国', '新加坡', '马来西亚',
            # 社会细分场景
            '疫情', '疫苗', '核酸', '防控', '政策', '法规', '法律', '维权',
            '反腐', '环保', '污染', '灾害', '地震', '洪水', '火灾', '救援',
            '交通', '事故', '车祸', '航班', '列车', '地铁', '公交',
            '教育', '学校', '考试', '高考', '中考', '考研', '留学',
            '就业', '失业', '工资', '社保', '医保', '养老'],
    '生活': ['健康', '美食', '情感', '数码', '科技', '生活', '日常',
            # 科技数码企业/IP
            '苹果', '华为', '小米', 'OPPO', 'vivo', '荣耀', '三星', '联想',
            '华硕', '戴尔', '惠普', '微软', '谷歌', '亚马逊', '特斯拉',
            '比亚迪', '蔚来', '理想', '小鹏', '极氪', '问界',
            'iPhone', 'iPad', 'Mac', '华为Mate', '华为P系列', '小米14', '红米',
            'AirPods', 'Apple Watch', '智能手表', '手环', '耳机', '音箱',
            '电脑', '笔记本', '平板', '手机', '相机', '镜头', '无人机',
            # 生活服务场景
            '外卖', '快递', '电商', '网购', '淘宝', '京东', '拼多多', '抖音',
            '快手', '微信', '支付宝', '支付', '转账', '理财', '银行',
            '租房', '买房', '装修', '家电', '冰箱', '空调', '洗衣机', '电视',
            '做饭', '菜谱', '餐厅', '奶茶', '咖啡', '火锅', '烧烤', '食材',
            '健身', '运动', '减肥', '瑜伽', '跑步', '游泳', '健身房'],
    '体育': ['比赛', '球队', '球员', '体育', '赛事', '冠军',
            '足球', '篮球', '排球', '网球', '乒乓球', '羽毛球', '游泳',
            '田径', '体操', '举重', '拳击', ' MMA ', '电竞', '英雄联盟',
            '王者荣耀', '世界杯', '欧洲杯', '奥运会', '亚运会', '全运会',
            'C罗', '梅西', '詹姆斯', '库里', '杜兰特', '朱婷', '马龙', '孙颖莎'],
    '文化': ['书籍', '文化', '历史', '艺术', '展览', '博物馆',
            '读书', '小说', '散文', '诗歌', '作家', '出版社',
            '绘画', '书法', '雕塑', '摄影', '美术馆', '画廊',
            '历史', '文物', '考古', '非遗', '传统', '民俗', '节日',
            '电影', '纪录片', '动画', '动漫', '漫画', '二次元']
}
    
    def classify_by_content(content):
        content = str(content).lower()
        matched_domains = []
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in content for keyword in keywords):
                matched_domains.append(domain)
        
        if len(matched_domains) == 0:
            return '其他', ['其他'], False
        elif len(matched_domains) == 1:
            return matched_domains[0], [], False
        else:
            return matched_domains[0], matched_domains[1:], True
    
    df[['预测主分类', '预测次要分类', '是否跨领域']] = df['热搜内容'].apply(
        lambda x: pd.Series(classify_by_content(x))
    )
    
    # 2. 内容特征提取
    df['内容长度'] = df['热搜内容'].apply(lambda x: len(str(x).strip()))
    df['词语数量'] = df['热搜内容'].apply(lambda x: len(str(x).split()))
    
    # 提取高频关键词
    all_words = []
    for content in df['热搜内容']:
        words = str(content).split()
        all_words.extend([word for word in words if len(word) > 1])
    
    top_keywords = Counter(all_words).most_common(10)
    top_keyword_list = [keyword for keyword, count in top_keywords]
    
    df['是否包含高频词'] = df['热搜内容'].apply(
        lambda x: any(keyword in str(x) for keyword in top_keyword_list)
    )
    
    # 3. 数据时间标记
    df['数据清洗时间'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 最终字段
    final_columns = [
        '热搜排名', '预测主分类', '预测次要分类', '是否跨领域',
        '热搜内容', '内容长度', '词语数量', '是否包含高频词',
        '热搜热度', '数据清洗时间'
    ]
    
    # 保存结果
    df[final_columns].to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 总热搜数据清洗完成")
    print(f"📁 输出路径: {output_path}")
    print(f"📊 预测分类分布: {df['预测主分类'].value_counts().to_dict()}")
    print(f"🔥 高频关键词Top10: {top_keywords}")
    
    return df[final_columns]