import json
import os

def build_valor_lake():
    print("🌊 正在构建 VALOR-32K 数据湖...")
    
    # 你下载的 valor 文件名
    valor_files = ['desc_train.json', 'desc_val.json', 'desc_test.json'] 
    valor_lake = {}

    for file_name in valor_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # VALOR 的结构是 [{"video_id": "...", "desc": "..."}, ...]
                for item in data:
                    vid = item.get("video_id")
                    desc = item.get("desc")
                    if vid and desc:
                        # 存入字典，用 video_id 作为身份证
                        valor_lake[vid] = desc

    # 保存为干净的数据湖文件
    with open('valor_datalake.json', 'w', encoding='utf-8') as f:
        # ensure_ascii=False 确保如果有特殊字符能正常显示
        json.dump(valor_lake, f, ensure_ascii=False, indent=4)
    
    print(f"✅ VALOR 数据湖构建完成！共收集 {len(valor_lake)} 条数据。")

# 运行
build_valor_lake()