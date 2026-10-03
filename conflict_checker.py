import json

def check_skincare_conflicts(current_data, cabinet_products, current_prod_name="目前產品"):
    """
    檢查目前產品與保養品櫃（Cabinet）內既有產品的成分衝突與重複功效，以及單品內部潛在干擾
    """
    conflicts = []
    
    # 取得目前產品的文字內容（全小寫以方便比對）
    current_text = json.dumps(current_data, ensure_ascii=False).lower()

    # --- 1. 單一產品內部的潛在衝突檢驗 ---
    # Niacinamide (菸鹼醯胺) + Ascorbic Acid (原型維他命C)
    if ("niacinamide" in current_text or "菸鹼醯胺" in current_text) and \
       ("ascorbic acid" in current_text or "抗壞血酸" in current_text or "維他命c" in current_text or "維生素c" in current_text):
        conflicts.append({
            "level": "warning",
            "title": "⚠️ 單品內高濃度菸鹼醯胺與維他命 C 組合",
            "msg": f"【{current_prod_name}】配方中同時包含菸鹼醯胺 (Niacinamide) 與維他命 C (Ascorbic Acid) 相關成分。敏感肌初次使用可能容易引起短暫皮膚泛紅或刺痛感，建議先於耳後局部測試。"
        })

    # 酸類 + A醇 (單品內)
    if ("acid" in current_text or "酸" in current_text) and ("retinol" in current_text or "a醇" in current_text or "視黃醇" in current_text):
        conflicts.append({
            "level": "danger",
            "title": "🚨 高刺激酸類與 A 醇成分疊加",
            "msg": f"【{current_prod_name}】同時含有酸類剝落成分與維生素 A 衍生物，質地較為刺激，請特別留意肌膚屏障健康。"
        })

    # --- 2. 與保養品櫃既有產品的跨產品衝突比對 ---
    if not cabinet_products:
        return conflicts

    for p in cabinet_products:
        # 解包資料庫欄位 (p_id, p_name, p_cat, p_tags_str, p_data_str, p_img_url, p_time)
        if len(p) >= 5:
            p_name = p[1]
            p_data_str = p[4]
        else:
            continue
        
        # 避免與自己比對
        if p_name == current_prod_name:
            continue
            
        try:
            p_data = json.loads(p_data_str) if isinstance(p_data_str, str) else p_data_str
            other_text = json.dumps(p_data, ensure_ascii=False).lower()
        except Exception:
            continue

        # 衝突 1：酸類與 A 醇跨產品疊擦
        if ("acid" in current_text or "酸" in current_text) and ("retinol" in other_text or "a醇" in other_text or "視黃醇" in other_text):
            conflicts.append({
                "level": "warning",
                "title": f"⚠️ 留意酸類與 A 醇疊擦風險 ({p_name})",
                "msg": f"【{current_prod_name}】與保養品櫃中的【{p_name}】分別含有酸類與維生素 A 衍生物，建議分開在早晚或隔天交替使用，避免角質過度剝落。"
            })

        # 衝突 2：高濃度菸鹼醯胺與維他命 C 跨產品疊擦
        if ("niacinamide" in current_text or "菸鹼醯胺" in current_text) and ("ascorbic acid" in other_text or "抗壞血酸" in other_text or "維他命c" in other_text):
            conflicts.append({
                "level": "warning",
                "title": f"⚠️ 留意菸鹼醯胺與原型維他命 C 疊擦 ({p_name})",
                "msg": f"【{current_prod_name}】與【{p_name}】分別含有菸鹼醯胺與維他命 C，若高濃度同時塗抹可能對敏感肌造成刺激，建議間隔時間使用。"
            })

    return conflicts