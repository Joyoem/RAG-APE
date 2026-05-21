import json
import os

def build_videoa11y_lake():
    print("🌊 正在构建 VideoA11y 黄金数据湖...")
    
    # 如果官方给你的是分好 train/val/test 的，就填入这三个文件名
    # 如果你下载的是一个包含 4 万条的大文件，列表里只写那一个文件名即可，比如 ['VideoA11y_40k.json']
    videoa11y_files = ['VideoA11y_train.json', 'VideoA11y_val.json', 'VideoA11y_test.json'] 

    videoa11y_lake = {}

    for file_name in videoa11y_files:
        if os.path.exists(file_name):
            print(f"📄 正在读取 {file_name} ...")
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 遍历列表中的每一个字典
                for item in data:
                    vid = item.get("Video_ID")
                    category = item.get("Video_Category", "Unknown")
                    desc = item.get("Desc", "")
                    
                    if vid and desc:
                        # 完美保留原有结构，用 Video_ID 作为“身份证号”(Key)
                        videoa11y_lake[vid] = {
                            "Category": category,
                            "Golden": desc
                        }

    # 保存为极其干净的黄金数据湖文件
    with open('videoa11y_datalake.json', 'w', encoding='utf-8') as f:
        json.dump(videoa11y_lake, f, ensure_ascii=False, indent=4)
    
    print(f"✅ VideoA11y 数据湖构建完成！共收集 {len(videoa11y_lake)} 条满分黄金数据。")

if __name__ == "__main__":
    build_videoa11y_lake()