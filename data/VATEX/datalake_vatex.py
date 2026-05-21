import json
import os

def build_vatex_lake():
    print("🌊 正在构建 VATEX 双语数据湖...")
    
    vatex_files = ['vatex_training_v1.0.json', 'vatex_validation_v1.0.json', 'vatex_public_test_english_v1.1.json']
    vatex_lake = {}

    for file_name in vatex_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # VATEX 的结构是 {"videoID": "...", "enCap": [...], "chCap": [...]}
                for item in data:
                    vid = item.get("videoID")
                    
                    # 提取第一句英文，如果没有就留空
                    en_draft = item["enCap"][0] if item.get("enCap") else ""
                    # 提取第一句中文，如果没有就留空
                    zh_draft = item["chCap"][0] if item.get("chCap") else ""
                    
                    if vid:
                        vatex_lake[vid] = {
                            "draft_en": en_draft,
                            "draft_zh": zh_draft
                        }

    # 保存为干净的数据湖文件
    with open('vatex_datalake.json', 'w', encoding='utf-8') as f:
        # ⚠️ 这里非常关键：ensure_ascii=False 才能让保存的 JSON 显示真实的中文汉字！
        json.dump(vatex_lake, f, ensure_ascii=False, indent=4)
    
    print(f"✅ VATEX 数据湖构建完成！共收集 {len(vatex_lake)} 条双语数据。")

# 运行
build_vatex_lake()