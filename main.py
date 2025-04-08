import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------- 常量与动作库 ------------------- #
DATA_FILE = "workout_log.csv"

BODY_PARTS = ["胸部", "背部", "肩部", "腿部", "二头肌", "三头肌"]

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

# 判断动作是否为单边
def is_single_side(exercise_name, major_muscle):
    for cat, sides in EXERCISES[major_muscle].items():
        for side, exercises in sides.items():
            for ex in exercises:
                full_name = f"{ex}（{cat}/{side}）"
                if full_name == exercise_name:
                    return side == "单边"
    return False  # 默认返回 False，避免误判

# 获取该动作最新的重量
def get_latest_weight(exercise_name):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # 获取该动作的最新一条记录（按时刻排序）
        latest_record = df[df['动作'] == exercise_name].sort_values(by="时刻", ascending=False).head(1)
        if not latest_record.empty:
            return float(latest_record['每次重量'].values[0])
    return 0  # 如果没有记录，默认重量为0

# 获取今日的训练记录
def get_today_workouts():
    today = datetime.today().strftime("%Y-%m-%d")  # 获取今日日期，格式为 '2025-04-08'
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # 将“时刻”列转换为 datetime 类型并筛选当天的数据
        df['时刻'] = pd.to_datetime(df['时刻'])
        today_records = df[df['时刻'].dt.strftime("%Y-%m-%d") == today]
        return today_records
    return pd.DataFrame()  # 如果没有记录，返回空 DataFrame

def add_a_record(major_or_assist, key_suffix=""):
    ex_name_raw = st.selectbox("选择动作", major_exercise_list, key=f"selected_exercise_{key_suffix}", index=None)
    if ex_name_raw:
        is_single_side = "单边" in ex_name_raw
        exercise_type = ex_name_raw.split("｜")[1].strip().split("｜")[0]  # 获取动作类型：哑铃/杠铃/器械/自重
        if "单边" in ex_name_raw:
            col_l, col_r = st.columns(2)
            # 获取默认重量
            latest_weight_l = get_latest_weight(ex_name_raw + "（左）")
            latest_weight_r = get_latest_weight(ex_name_raw + "（右）")

            with col_l:
                weight_l = st.number_input("左侧重量 (kg)", min_value=0.0, value=float(latest_weight_l),
                                           step=2.0)  # step为浮动类型
                reps_l = st.number_input("左侧次数", min_value=1, value=8)
            with col_r:
                weight_r = st.number_input("右侧重量 (kg)", min_value=0.0, value=float(latest_weight_r),
                                           step=2.0)  # step为浮动类型
                reps_r = st.number_input("右侧次数", min_value=1, value=8)
        else:
            # 获取默认重量
            latest_weight = get_latest_weight(ex_name_raw)
            col_l, col_r = st.columns(2)
            with col_l:
                if exercise_type == "哑铃":
                    weight = st.number_input("该组重量 (kg)", min_value=0.0, value=float(latest_weight), step=2.0)
                elif exercise_type == "杠铃":
                    weight = st.number_input("该组重量 (kg)", min_value=0.0, value=float(latest_weight),
                                             step=2.5)  # make sure it's float
                elif exercise_type == "器械":
                    weight = st.number_input("该组重量 (kg)", min_value=0.0, value=float(latest_weight),
                                             step=5.0)  # make sure it's float
                else:
                    weight = 0  # 自重动作不显示重量输入
            if exercise_type != "自重":
                with col_r:
                    reps = st.number_input("该组次数", min_value=1, value=8)
            else:
                reps = st.number_input("该组次数", min_value=1, value=8)

        add_clicked = st.button("确认动作")

        if add_clicked:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时刻
            if is_single_side:
                if weight_l and reps_l:
                    record_l = {
                        "时刻": now,
                        "主训部位": major_muscle,
                        "辅训部位": asist_muscle,
                        "动作": ex_name_raw + "（左）",
                        "每组重量": weight_l,
                        "每组次数": reps_l,
                        "是否主训": major_or_assist,
                    }
                    df = pd.read_csv(DATA_FILE)
                    df = df.append(record_l, ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.session_state.exercise_sets.append(record_l)

                if weight_r and reps_r:
                    record_r = {
                        "时刻": now,
                        "主训部位": major_muscle,
                        "辅训部位": asist_muscle,
                        "动作": ex_name_raw + "（右）",
                        "每组重量": weight_r,
                        "每组次数": reps_r,
                        "是否主训": major_or_assist,
                    }
                    df = pd.read_csv(DATA_FILE)
                    df = df.append(record_r, ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.session_state.exercise_sets.append(record_r)

            else:
                if ex_name_raw and weight and reps:
                    record = {
                        "时刻": now,
                        "主训部位": major_muscle,
                        "辅训部位": asist_muscle,
                        "动作": ex_name_raw,
                        "每组重量": weight,
                        "每组次数": reps,
                        "是否主训": major_or_assist,
                    }
                    df = pd.read_csv(DATA_FILE)
                    df = df.append(record, ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.session_state.exercise_sets.append(record)

            st.success("✅ 动作已记录")

def extract_date(timestamp):
    return timestamp.strftime('%Y-%m-%d')


# 初始化 CSV 文件
def init_csv():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(
            columns=["时刻", "主训部位", "辅训部位", "动作", "每组重量", "每组次数", "是否主训"])
        df.to_csv(DATA_FILE, index=False)

init_csv()

st.title("🏋️ GymSPY")
tab1, tab2, tab3 = st.tabs(["记录训练", "今日数据", "数据总结"])
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        major_muscle = st.selectbox("主训部位", BODY_PARTS, index=None)
    with col2:
        asist_muscle = st.selectbox("辅训部位", BODY_PARTS, index=None)
        if major_muscle and asist_muscle and major_muscle == asist_muscle:
            st.error("主训部位和辅训部位不能相同，请重新选择。")
            asist_muscle = None

    if major_muscle:
        st.markdown("### 记录训练动作")

        st.markdown(f"#### 💪 主训部位：{major_muscle}")
        major_exercise_list = [
            f"{ex}｜{cat}｜{sd}"
            for cat, sides in EXERCISES[major_muscle].items()
            for sd, exs in sides.items()
            for ex in exs
        ]
        if "exercise_sets" not in st.session_state:
            st.session_state.exercise_sets = []
        st.markdown("##### 📝 添加一组训练记录")
        add_a_record("是", key_suffix="major")

        if asist_muscle:
            st.markdown(f"#### 🤝 辅训部位：{asist_muscle}")
            major_exercise_list = [
                f"{ex}｜{cat}｜{sd}"
                for cat, sides in EXERCISES[asist_muscle].items()
                for sd, exs in sides.items()
                for ex in exs
            ]
            if "exercise_sets" not in st.session_state:
                st.session_state.exercise_sets = []
            st.markdown("##### 📝 添加一组训练记录")
            add_a_record("否", key_suffix="assist")

with tab2:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['时刻'] = pd.to_datetime(df['时刻'])
    else:
        st.warning("暂无训练数据")
        st.stop()

    available_dates = sorted(df["时刻"].dt.date.unique(), reverse=True)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    selected_date = st.date_input("选择日期", value=datetime.today().date())
    df_day = df[df["时刻"].dt.date == selected_date]
    st.markdown(f"### 📅 {selected_date.strftime('%Y 年 %m 月 %d 日')} 的训练记录")

    # 主训部位展示
    for muscle in df_day["主训部位"].dropna().unique():
        st.markdown(f"#### 💪 主训部位：{muscle}")
        df_muscle = df_day[df_day["主训部位"] == muscle]

        for exercise in df_muscle["动作"].unique():
            st.markdown(f"##### ✨{exercise}")
            df_ex = df_muscle[df_muscle["动作"] == exercise].reset_index(drop=True)

            for i in range(0, len(df_ex), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(df_ex):
                        row = df_ex.iloc[i + j]
                        cols[j].markdown(f"**{row['每组重量']}KG × {row['每组次数']}个**")

    # 辅训部位展示
    for muscle in df_day["辅训部位"].dropna().unique():
        st.markdown(f"#### 🧩 辅训部位：{muscle}")
        df_muscle = df_day[df_day["辅训部位"] == muscle]

        for exercise in df_muscle["动作"].unique():
            st.markdown(f"##### ✨{exercise}")
            df_ex = df_muscle[df_muscle["动作"] == exercise].reset_index(drop=True)

            for i in range(0, len(df_ex), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(df_ex):
                        row = df_ex.iloc[i + j]
                        cols[j].markdown(f"**{row['每组重量']}KG × {row['每组次数']}个**")

with tab3:
    # 获取 CSV 数据
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['时刻'] = pd.to_datetime(df['时刻'])
    else:
        st.warning("暂无训练数据")
        st.stop()

    cola, colb = st.columns(2)
    with cola:
        start_date = st.date_input("开始日期", min_value=df['时刻'].min().date(), max_value=df['时刻'].max().date(),
                                   value=df['时刻'].min().date())
    with colb:
        end_date = st.date_input("结束日期", min_value=df['时刻'].min().date(), max_value=df['时刻'].max().date(),
                                 value=df['时刻'].max().date())
    # 过滤数据
    df_filtered = df[(df['时刻'].dt.date >= start_date) & (df['时刻'].dt.date <= end_date)]
    # 训练频率统计
    st.markdown("### 🏋️‍♂️ 训练频率统计")

    # 转换日期
    df_filtered['日期'] = pd.to_datetime(df_filtered['时刻']).dt.date

    # 统计每个部位参与训练的天数（按日期去重）
    freq_data = {}
    for muscle in BODY_PARTS:
        days_main = df_filtered[df_filtered['主训部位'] == muscle][['日期']]
        days_assist = df_filtered[df_filtered['辅训部位'] == muscle][['日期']]

        all_days = pd.concat([days_main, days_assist]).drop_duplicates()
        freq_data[muscle] = len(all_days)

    # 显示每个部位的训练天数
    cols = st.columns(3)  # 自定义列数
    for idx, (muscle, days) in enumerate(freq_data.items()):
        with cols[idx % 3]:
            st.metric(label=f"💪 {muscle}", value=f"{days} 天")

    # 选择动作并展示其每日最大重量及对应次数
    st.markdown("### 动作每日最大重量及对应次数变化")
    selected_exercise = st.selectbox("选择动作", df_filtered['动作'].unique())

    # 过滤出选定动作的数据
    df_exercise = df_filtered[df_filtered['动作'] == selected_exercise]

    # 计算每一天的最大重量和对应的次数
    df_exercise['日期'] = df_exercise['时刻'].apply(extract_date)
    df_max_weight = df_exercise.groupby('日期').agg({'每组重量': 'max', '每组次数': 'last'}).reset_index()

    # 显示最大重量与次数变化的图表
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        specs=[[{"secondary_y": True}]]
    )

    # 最大重量折线图（主 y 轴）
    fig.add_trace(
        go.Scatter(
            x=df_max_weight['日期'],
            y=df_max_weight['每组重量'],
            mode='lines+markers',
            name='最大重量 (kg)',
            line=dict(color='blue')
        ),
        secondary_y=False
    )

    # 最大次数柱状图（副 y 轴）
    fig.add_trace(
        go.Bar(
            x=df_max_weight['日期'],
            y=df_max_weight['每组次数'],
            name='最大次数',
            marker=dict(color='red'),
            opacity=0.6
        ),
        secondary_y=True
    )

    # 设置布局
    fig.update_layout(
        title=f"{selected_exercise} 每日最大重量及次数变化",
        xaxis_title="日期",
        yaxis_title="最大重量 (kg)",
        yaxis2_title="最大次数",
        template="plotly_dark",
        barmode='overlay'  # 样式可以是 overlay 或 relative，看你喜好
    )

    # 显示图表
    st.plotly_chart(fig)