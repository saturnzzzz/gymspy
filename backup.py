from docx import Document
from datetime import datetime, timedelta
import csv
import re

# === 路径设置 ===
doc_path = "健身记录 (1).docx"  # 修改为你的实际路径
csv_path = "训练记录整理.txt"

# === 定义动作字典 ===
EXERCISES = {
    "胸部": {
        "哑铃": {
            "双边": ["哑铃平板卧推", "哑铃上斜卧推", "哑铃飞鸟", "哑铃飞鸟与斯万夹胸组合训练"],
        },
        "杠铃": {
            "双边": ["杠铃平板卧推", "杠铃上斜卧推", "斯万开胸"],
        },
        "器械": {
            "双边": ["史密斯平板卧推", "史密斯上斜卧推", "固定门架开胸", "器械胸推", "蝴蝶机夹胸"],
        },
        "自重": {
            "双边": ["俯卧撑"],
        }
    },
    "三头肌": {
        "哑铃": {"双边": ["哑铃俯身臂屈伸"], "单边": ["单臂哑铃过头伸展"]},
        "杠铃": {"双边": ["杠铃窄握卧推", "仰卧杠铃臂屈伸"]},
        "器械": {"双边": ["绳索下压", "直杠正手下压", "直杠反手下压"]}
    },
    "肩部": {
        "哑铃": {"双边": ["坐姿哑铃推举", "哑铃侧平举", "站姿哑铃侧平举", "哑铃前平举","哑铃左右前平举", "哑铃复合推举", "哑铃后肩训练", "哑铃俯身飞鸟", "阿诺德推举", "哑铃复合推举搭配哑铃侧平举", "哑铃前平举搭配哑铃俯身飞鸟训练"]},
        "杠铃": {"双边": ["杠铃推举"]},
        "器械": {"双边": ["史密斯推肩", "上斜推肩", "绳索后拉"]}
    },
    "二头肌": {
        "哑铃": {"双边": ["坐姿哑铃弯举", "哑铃二头弯举", "锤式弯举", "集中弯举","站姿哑铃弯举"]},
        "杠铃": {"双边": ["杠铃弯举", "EZ杠弯举"]},
        "器械": {"双边": ["钢线二头弯举"]}
    },
    "背部": {
        "哑铃": {"双边": ["哑铃划船","哑铃硬拉"], "单边": ["单臂哑铃划船"]},
        "杠铃": {"双边": ["杠铃硬拉", "杠铃划船", "T杠划船"]},
        "器械": {"双边": ["坐姿划船", "高位下拉", "低位划船", "引体向上"]}
    },
    "腿部": {
        "哑铃": {"双边": ["哑铃深蹲", "高脚背深蹲"], "单边": ["交替弓箭步蹲"]},
        "杠铃": {"双边": ["杠铃深蹲", "前步蹲", "罗马尼亚硬拉"]},
        "器械": {"双边": ["史密斯深蹲", "腿举", "腿屈伸", "腿弯举", "坐姿蹲腿"]},
        "自重": {"双边": ["臀桥"], "单边": ["保加利亚深蹲"]}
    }
}

def build_exercise_mapping():
    """构建动作到分类的映射表，增加器械和单双边信息"""
    mapping = {}
    for muscle, categories in EXERCISES.items():
        for category, subtypes in categories.items():
            for subtype, exercises in subtypes.items():
                for exercise in exercises:
                    # 处理组合动作
                    if '➕' in exercise:
                        combo_exercises = exercise.split('➕')
                        for e in combo_exercises:
                            e = e.strip()
                            mapping[e] = {
                                "muscle": muscle,
                                "category": category,
                                "subtype": subtype
                            }
                    else:
                        mapping[exercise] = {
                            "muscle": muscle,
                            "category": category,
                            "subtype": subtype
                        }
    return mapping


def parse_reps(reps_part):
    """
    解析次数部分，提取所有数字（单位为“个”）。
    :param reps_part: 次数描述字符串
    :return: 次数列表
    """
    reps = []
    # 匹配数字 + "个" 的模式
    matches = re.findall(r'(\d+)\s*个', reps_part)
    for match in matches:
        reps.append(match.strip())
    return reps


def parse_training_records(content):
    """解析训练记录内容，并输出未知动作及其日期"""
    records = []
    unknown_actions = []  # 用于存储未知动作及其日期
    exercise_map = build_exercise_mapping()
    current_date = None
    main_part = sub_part = None
    current_exercise = None
    timestamp = None
    time_increment = 0

    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('健身记录'):
            continue

        # 解析日期行（格式：1月16日：胸部和三头肌 或 4月8日：肩部）
        if '月' in line and '日' in line and '：' in line:
            date_part, parts = line.split('：', 1)

            # 处理日期格式（兼容无空格的情况）
            try:
                # 将“4月8日”转换为“4 月 8 日”
                formatted_date = date_part.replace('月', ' 月 ').replace('日', ' 日 ')
                current_date = datetime.strptime(formatted_date + ' 2025', '%m 月 %d 日 %Y')
            except ValueError as e:
                print(f"日期解析失败: {date_part}，错误信息: {e}")
                continue

            # 处理主训和辅训部位
            if '和' in parts:
                main_part, sub_part = [p.strip() for p in parts.split('和')]
            elif parts.strip():  # 如果只有主训部位
                main_part = parts.strip()
                sub_part = ""
            else:
                main_part = sub_part = ""  # 主训和辅训部位均为空

            time_increment = 0  # 重置时间增量

        # 解析动作行（以中文字符开头且不包含数字）
        elif line and line[0] not in '0123456789+（' and '：' not in line:
            current_exercise = line.split('(')[0].strip()
            time_increment += 1  # 每个新动作增加时间间隔

        # 解析重量和次数行（以数字或特殊符号开头）
        elif line.startswith(('+', '（')) or line[0].isdigit():
            try:
                weight_part, reps_part = line.split('：', 1)
                weight_part = weight_part.strip()
                reps_part = reps_part.strip()

                # 使用 parse_reps 函数解析次数
                reps = parse_reps(reps_part)

                if not reps:
                    print(f"警告：动作 {current_exercise} 缺少有效次数信息")
                    continue

                # 处理组合动作
                exercises = []
                if '➕' in current_exercise:
                    exercises = [e.strip() for e in current_exercise.split('➕')]
                else:
                    exercises = [current_exercise]

                # 生成时间戳
                timestamp = current_date + timedelta(minutes=time_increment)

                for exercise in exercises:
                    exercise_info = exercise_map.get(exercise,
                                                     {"muscle": "未知", "category": "未知", "subtype": "未知"})
                    muscle_group = exercise_info["muscle"]
                    is_main = muscle_group == main_part if main_part else False

                    # 检查是否为未知动作
                    if exercise_info["muscle"] == "未知":
                        unknown_actions.append((exercise, current_date.strftime('%Y-%m-%d')))

                    formatted_exercise = f"{exercise}｜{exercise_info['category']}｜{exercise_info['subtype']}"

                    for rep in reps:
                        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        records.append([
                            timestamp_str,
                            main_part,
                            sub_part,
                            formatted_exercise,
                            weight_part,
                            rep,
                            "是" if is_main else "否"
                        ])
                        timestamp += timedelta(seconds=30)
            except Exception as e:
                print(f"解析失败: {line}, 错误信息: {e}")

    return records, unknown_actions



def save_to_csv(records, filename):
    """保存为CSV文件"""
    headers = [
        "时刻", "主训部位", "辅训部位", "动作", "每组重量", "每组次数", "是否主训"
    ]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)


# 输出未知动作及其日期
if __name__ == "__main__":
    # 读取原始数据（需要将docx转换为文本）
    with open("训练记录整理.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # 解析并保存
    records, unknown_actions = parse_training_records(content)
    save_to_csv(records, "fitness_data.csv")

    # 输出未知动作及其日期
    if unknown_actions:
        print("以下是未识别的动作及其日期：")
        for action, date in unknown_actions:
            print(f"{action} - {date}")
    else:
        print("所有动作均已正确识别，没有未知动作。")