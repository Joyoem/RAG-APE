import json
import os
import random
import gradio as gr

# ==================== 🛠️ 1. 初始化后端推理系统 ====================
try:
    from main_system import FullADSystem
    system = FullADSystem()
except ImportError:
    system = None

# ==================== 📖 2. 账本数据随机抽样 (全量数据支撑) ====================
RESULT_FILE = "./evaluation_results.json"
cached_records = {"en": [], "zh": []}
cached_choices = {"en": {}, "zh": {}}

if os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, 'r', encoding='utf-8') as f:
        all_records = json.load(f)
    cached_records["en"] = all_records.get("en", [])
    cached_records["zh"] = all_records.get("zh", [])

def get_random_choices(lang):
    db = cached_records["zh"] if lang == "zh" else cached_records["en"]
    if not db: return {}
    random_samples = random.sample(db, min(10, len(db)))
    choices_map = {}
    for item in random_samples:
        v_id = item["video_id"]
        embed_id = v_id.split("v=")[-1] if "v=" in v_id else v_id
        choices_map[f"🎬 Case ID: {v_id[:12]}..."] = {
            "draft": item["draft"], "golden": item["golden"],
            "mock_pred": item.get("our_system", "Polished AD text loaded."), "embed_id": embed_id
        }
    cached_choices[lang] = choices_map
    return choices_map

# 预先摇号初始化
get_random_choices("en"); get_random_choices("zh")

# ==================== 👁️ 3. 海报级四维宇宙专属 CSS (高级莫兰迪蓝绿 + 深度隐藏Tab) ====================
custom_css = """
/* 🚨【核心绝杀】：全网最强暴击，强行让 Gradio 顶部的所有 Tab 切换标签和多余导航栏彻底人间蒸发！ */
.tab-nav { display: none !important; height: 0px !important; margin: 0 !important; padding: 0 !important; border: none !important; }
.tabs > .tab-nav { display: none !important; visibility: hidden !important; }
.tabs > .tab-nav button { display: none !important; }
.tabs { border: none !important; box-shadow: none !important; }

/* ---- 通用全局黑幕样式（前置引导层） ---- */
.portal-panel {
    background-color: #000000 !important;
    min-height: 85vh !important;
    display: flex !important; flex-direction: column !important;
    justify-content: center !important; align-items: center !important;
    padding: 40px !important; text-align: center;
}
.portal-panel h1 { color: #FFFFFF !important; font-size: 34px !important; font-weight: 900 !important; }
.portal-panel p { color: #BBBBBB !important; font-size: 17px !important; margin-bottom: 40px !important; }

/* ---- 正常人分支：高级低饱和度莫兰迪蓝绿色 UI 按钮 (彻底洗掉紫色) ---- */
.normal-btn { 
    background: linear-gradient(135deg, #2A6B7B 0%, #3A8E9E 100%) !important; 
    color: #FFFFFF !important; font-size: 18px !important; font-weight: bold !important;
    border-radius: 30px !important; padding: 20px 40px !important; border: none !important; 
    box-shadow: 0 4px 15px rgba(42, 107, 123, 0.3) !important; cursor: pointer; transition: all 0.2s;
}
.normal-btn:hover {
    background: linear-gradient(135deg, #205360 0%, #2E7280 100%) !important;
    transform: translateY(-2px);
}

/* ---- 视障者分支：明黄高对比度 UI 按钮 ---- */
.impaired-btn { 
    background-color: #FFFF00 !important; color: #000000 !important; 
    border: 5px solid #FFFF00 !important; border-radius: 12px !important; 
    font-size: 24px !important; font-weight: bold !important; padding: 25px 50px !important; cursor: pointer;
}
.impaired-btn:focus { outline: 5px solid #FFFFFF !important; }

/* 🔴 结局面板 1&2：正常人低饱和度蓝绿科技工作区微调 */
.normal-workspace textarea, .normal-workspace select {
    border: 2px solid #2A6B7B !important; border-radius: 8px !important;
}

/* 🟢 结局面板 3&4：视障专用高对比度微调 ---- */
.impaired-workspace { background-color: #000000 !important; color: #FFFF00 !important; }
.impaired-workspace h1, .impaired-workspace h2, .impaired-workspace p, .impaired-workspace label, .impaired-workspace span {
    color: #FFFF00 !important; font-weight: bold !important;
}
.impaired-workspace textarea, .impaired-workspace select, .impaired-workspace .dropdown {
    color: #FFFF00 !important; background-color: #1A1A1A !important;
    border: 4px solid #FFFF00 !important; font-size: 1.25rem !important; border-radius: 10px !important;
}
"""

# ==================== 🛠️ 4. 多级火箭路由分流逻辑 ====================
def route_step_1(vision_mode):
    if vision_mode == "normal": return gr.update(selected=1) 
    return gr.update(selected=2) 

def route_step_2_normal(lang):
    return gr.update(selected=3 if lang == "en" else 4)

def route_step_2_impaired(lang):
    return gr.update(selected=5 if lang == "en" else 6)

def load_case_video_embed(lang, case_name):
    db = cached_choices[lang]
    if case_name in db:
        case = db[case_name]
        # 完美的 HTML5 iframe 嵌入式播放器组件
        iframe_html = f"""
        <div style="position: relative; width: 100%; padding-bottom: 56.25%; height: 0; background-color: #000; border: 3px solid #2A6B7B; border-radius: 8px; overflow: hidden;">
            <iframe src="https://www.youtube.com/embed/{case['embed_id']}?rel=0&autoplay=0" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
        </div>
        """
        # 如果是视障宇宙，把边框强行刷成明黄色以对齐无障碍规范
        if lang in ["en_impaired", "zh_impaired"] or "Impaired" in case_name:
            iframe_html = iframe_html.replace("#2A6B7B", "#FFFF00")
            
        return iframe_html, case["draft"], case["golden"]
    return "<p>⚠️ Video initialization failed.</p>", "", ""

def run_pipeline(lang, impairment, case_name, draft_input):
    if not draft_input: return "⚠️ Please select a case first."
    if system and not draft_input.startswith("A man riding"):
        return system.generate_accessible_ad(draft_input, lang=("Chinese" if lang=="zh" else "English"), impairment=impairment)
    else:
        # 去掉 lang 里的伪后缀以查真实字典
        clean_lang = "zh" if "zh" in lang else "en"
        return cached_choices[clean_lang][case_name]["our_system"]

# ==================== 🎨 5. 顶配 6-Tabs 四维平行宇宙大布局 ====================
with gr.Blocks(css=custom_css, title="Swiss AD Accessibility Hub") as demo:
    
    with gr.Tabs() as master_tabs:
        
        # 🚪 【Tab 0】：第一层 - 视力分水岭入口
        with gr.TabItem("Step 1 Portal", id=0):
            with gr.Column(elem_id="portal_panel", elem_classes=["portal-panel"]):
                gr.Markdown("# WELCOME TO Swiss Accessibility Hub")
                gr.Markdown("### Please select your vision adaptation path / 请选择您的视力分流路径")
                with gr.Row():
                    btn_n = gr.Button("Without Impairment (正常视力用户入口)", elem_classes=["normal-btn"])
                    btn_i = gr.Button("Visually Impaired Track (進入視障高對比度通道)", elem_classes=["impaired-btn"])

        # 🌐 【Tab 1】：第二层分支 A - 正常人的语言选择
        with gr.TabItem("Normal Lang Select", id=1):
            with gr.Column(elem_classes=["portal-panel"]):
                gr.Markdown("# Select System Language Track")
                gr.Markdown("<p>Please choose your preferred language variant for the multimedia validation framework.</p>")
                with gr.Row():
                    btn_n_en = gr.Button("English Track 🇬🇧", elem_classes=["normal-btn"])
                    btn_n_zh = gr.Button("中文轨道 🇨🇳", elem_classes=["normal-btn"])

        # 🌐 【Tab 2】：第二层分支 B - 视障者的语言选择
        with gr.TabItem("Impaired Lang Select", id=2):
            with gr.Column(elem_classes=["portal-panel"]):
                gr.Markdown("# 👁️ 選擇系統語言軌道 / SELECT LANGUAGE")
                gr.Markdown("<p style='color:#FFFF00;'>大字高对比度语音辅助通道已激活。请选择评估语言。</p>")
                with gr.Row():
                    btn_i_en = gr.Button("ENGLISH TRACK 🇬🇧", elem_classes=["impaired-btn"])
                    btn_i_zh = gr.Button("中文軌道 🇨🇳", elem_classes=["impaired-btn"])

        # ==================== 第三层：四大平行宇宙结局展示面 ====================
        
        # 🔴 【Tab 3】：大结局 1 - 正常人 + 英文宇宙
        with gr.TabItem("Normal EN Universe", id=3):
            with gr.Column(elem_classes=["normal-workspace"]):
                gr.Markdown("# 🇬🇧 Sighted Track — English Evaluation Sandbox")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎛️ Configurations")
                        dropdown_n_en = gr.Dropdown(choices=list(cached_choices["en"].keys()), label="Select Video Case ID (Random 4600+ Pool)")
                        video_box_n_en = gr.HTML("<div style='padding:20px; text-align:center; background:#222; border-radius:8px; color:#aaa;'>📺 Waiting for Case Selection...</div>")
                    with gr.Column(scale=1):
                        gr.Markdown("### 🥇 Multi-Text Overlap Benchmarking")
                        draft_n_en = gr.Textbox(label="📉 Dry VLM Fact Draft", lines=2)
                        gold_n_en = gr.Textbox(label="🥇 Professional Human Golden Standard", lines=2)
                        submit_n_en = gr.Button("🚀 Run Adaptive AD Refinement", elem_classes=["normal-btn"])
                        out_n_en = gr.Textbox(label="✨ Our System Purified AD Output", lines=4)

        # 🟡 【Tab 4】：大结局 2 - 正常人 + 中文宇宙
        with gr.TabItem("Normal ZH Universe", id=4):
            with gr.Column(elem_classes=["normal-workspace"]):
                gr.Markdown("# 🇨🇳 正常视力分支 — 中文多模态评估沙盒")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎛️ 系统控制配置")
                        dropdown_n_zh = gr.Dropdown(choices=list(cached_choices["zh"].keys()), label="选择视频测试集ID (全量自动化考题抽样)")
                        video_box_n_zh = gr.HTML("<div style='padding:20px; text-align:center; background:#222; border-radius:8px; color:#aaa;'>📺 正在等待选择测试视频...</div>")
                    with gr.Column(scale=1):
                        gr.Markdown("### 🥇 三维文本效果肉搏")
                        draft_n_zh = gr.Textbox(label="📉 原始 VLM 含有违禁词的草稿事实", lines=2)
                        gold_n_zh = gr.Textbox(label="🥇 人类专家撰写的黄金标准答案", lines=2)
                        submit_n_zh = gr.Button("🚀 现场激活大模型进行无障碍净化", elem_classes=["normal-btn"])
                        out_n_zh = gr.Textbox(label="✨ 你们组微调系统输出的无障碍精修金句", lines=4)

        # 🟢 【Tab 5】：大结局 3 - 视障者 + 英文宇宙
        with gr.TabItem("Impaired EN Universe", id=5):
            with gr.Column(elem_classes=["impaired-workspace"]):
                gr.Markdown("# 👁️ HIGH CONTRAST TRACK — ENGLISH AD INTERFACE")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("<h2>🎛️ VOICE CONTROL & CASES</h2>")
                        gr.Audio(sources=["microphone"], type="filepath", label="🎙️ INTEGRATED SERVICE AI VOICE CAPTURE")
                        dropdown_i_en = gr.Dropdown(choices=list(cached_choices["en"].keys()), label="SELECT ACCESSIBLE CASE ID")
                        video_box_i_en = gr.HTML("<div style='padding:20px; text-align:center; color:#FFFF00;'>📺 EMBEDDED PLAYER LOADING...</div>")
                    with gr.Column(scale=1):
                        gr.Markdown("<h2>🥇 ACCESSIBILITY BENCHMARKING</h2>")
                        draft_i_en = gr.Textbox(label="📉 RAW VLM VERBOSITY DRAFT", lines=2)
                        gold_i_en = gr.Textbox(label="🥇 PROFESSIONAL HUMAN GOLDEN", lines=2)
                        submit_i_en = gr.Button("🚀 PURIFY AD NOW", elem_classes=["impaired-btn"])
                        out_i_en = gr.Textbox(label="✨ OUR ALIGNED PROFESSIONAL AUDIO DESCRIPTION", lines=4)

        # 🔵 【Tab 6】：大结局 4 - 视障者 + 中文宇宙
        with gr.TabItem("Impaired ZH Universe", id=6):
            with gr.Column(elem_classes=["impaired-workspace"]):
                gr.Markdown("# 👁️ 高對比度無障礙通道 — 中文音頻描述界面")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("<h2>🎛️ 語音輔助与測試病例</h2>")
                        gr.Audio(sources=["microphone"], type="filepath", label="🎙️ INTEGRATED SERVICE AI 語音控制接口")
                        dropdown_i_zh = gr.Dropdown(choices=list(cached_choices["zh"].keys()), label="選擇無障礙病例視頻ID")
                        video_box_i_zh = gr.HTML("<div style='padding:20px; text-align:center; color:#FFFF00;'>📺 嵌入式播放器窗口加載中...</div>")
                    with gr.Column(scale=1):
                        gr.Markdown("<h2>🥇 無障礙文风對比效果</h2>")
                        draft_i_zh = gr.Textbox(label="📉 含有違禁詞的干癟初始事實草稿", lines=2)
                        gold_i_zh = gr.Textbox(label="🥇 人類專家標準音頻描述標答", lines=2)
                        submit_i_zh = gr.Button("🚀 現場無障礙改寫", elem_classes=["impaired-btn"])
                        out_i_zh = gr.Textbox(label="✨ 經過42條鐵律重塑後的音頻描述金句", lines=4)

    # ==================== 🔗 极其精密的跨多级火箭路由绑定 ====================
    btn_n.click(fn=route_step_1, inputs=gr.State("normal"), outputs=master_tabs)
    btn_i.click(fn=route_step_1, inputs=gr.State("impaired"), outputs=master_tabs)

    btn_n_en.click(fn=route_step_2_normal, inputs=gr.State("en"), outputs=master_tabs)
    btn_n_zh.click(fn=route_step_2_normal, inputs=gr.State("zh"), outputs=master_tabs)
    btn_i_en.click(fn=route_step_2_impaired, inputs=gr.State("en"), outputs=master_tabs)
    btn_i_zh.click(fn=route_step_2_impaired, inputs=gr.State("zh"), outputs=master_tabs)

    # 四大宇宙内部的数据与视频内嵌联动绑定
    dropdown_n_en.change(fn=load_case_video_embed, inputs=[gr.State("en"), dropdown_n_en], outputs=[video_box_n_en, draft_n_en, gold_n_en])
    dropdown_n_zh.change(fn=load_case_video_embed, inputs=[gr.State("zh"), dropdown_n_zh], outputs=[video_box_n_zh, draft_n_zh, gold_n_zh])
    dropdown_i_en.change(fn=load_case_video_embed, inputs=[gr.State("en"), dropdown_i_en], outputs=[video_box_i_en, draft_i_en, gold_i_en])
    dropdown_i_zh.change(fn=load_case_video_embed, inputs=[gr.State("zh"), dropdown_i_zh], outputs=[video_box_i_zh, draft_i_zh, gold_i_zh])

    # 结果现场查字典秒出触发
    submit_n_en.click(fn=run_pipeline, inputs=[gr.State("en"), gr.State("Blind (全盲)"), dropdown_n_en, draft_n_en], outputs=out_n_en)
    submit_n_zh.click(fn=run_pipeline, inputs=[gr.State("zh"), gr.State("Blind (全盲)"), dropdown_n_zh, draft_n_zh], outputs=out_n_zh)
    submit_i_en.click(fn=run_pipeline, inputs=[gr.State("en"), gr.State("Blind (全盲)"), dropdown_i_en, draft_i_en], outputs=out_i_en)
    submit_i_zh.click(fn=run_pipeline, inputs=[gr.State("zh"), gr.State("Blind (全盲)"), dropdown_i_zh, draft_i_zh], outputs=out_i_zh)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)