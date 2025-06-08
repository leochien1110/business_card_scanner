# translations.py - Internationalization support for Business Card Scanner

TRANSLATIONS = {
    "en": {
        # Main title and description
        "title": "📇 Business Card Scanner",
        "description": "Extract contact information from business card images",
        
        # Model section
        "vision_model": "🎯 Vision Model",
        "connection_testing": "🟡 Testing connection...",
        
        # Upload section
        "upload_label": "📁 Upload Business Cards",
        "use_raw_images": "📸 Use Raw Images (Higher Quality)",
        "custom_filename": "📝 Custom Filename (optional)",
        "filename_placeholder": "my_contacts.csv",
        
        # Buttons
        "start_processing": "🚀 Start Processing",
        "stop": "⏹️ Stop",
        
        # Preview section
        "image_preview": "### 🖼️ Image Preview",
        "uploaded_images": "Uploaded Images",
        
        # Results section
        "results": "### 📊 Results",
        "extracted_data": "Extracted Data",
        "download_csv": "💾 Download CSV",
        
        # Data fields
        "name": "name",
        "company": "company", 
        "title": "title",
        "phone": "phone",
        "email": "email",
        "address": "address",
        "handwriting_notes": "handwriting_notes",
        "other": "other",
        
        # Status messages
        "connected": "🟢 Connected",
        "failed": "🔴 Failed",
        "processing": "Processing...",
        "completed": "Completed",
        "stopped": "⏹️ Stopped"
    },
    
    "zh-tw": {
        # Main title and description
        "title": "📇 名片掃描器",
        "description": "從名片圖片中提取聯絡資訊",
        
        # Model section
        "vision_model": "🎯 視覺模型",
        "connection_testing": "🟡 測試連線中...",
        
        # Upload section
        "upload_label": "📁 上傳名片",
        "use_raw_images": "📸 使用原始圖片（更高品質）",
        "custom_filename": "📝 自訂檔案名稱（選用）",
        "filename_placeholder": "我的聯絡人.csv",
        
        # Buttons
        "start_processing": "🚀 開始處理",
        "stop": "⏹️ 停止",
        
        # Preview section
        "image_preview": "### 🖼️ 圖片預覽",
        "uploaded_images": "已上傳圖片",
        
        # Results section
        "results": "### 📊 結果",
        "extracted_data": "提取的資料",
        "download_csv": "💾 下載 CSV",
        
        # Data fields
        "name": "姓名",
        "company": "公司",
        "title": "職稱", 
        "phone": "電話",
        "email": "電子郵件",
        "address": "地址",
        "handwriting_notes": "手寫筆記",
        "other": "其他",
        
        # Status messages
        "connected": "🟢 已連線",
        "failed": "🔴 失敗",
        "processing": "處理中...",
        "completed": "完成",
        "stopped": "⏹️ 已停止"
    }
}

def get_text(key, lang="en"):
    """Get translated text for given key and language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

def get_headers(lang="en"):
    """Get translated column headers for the dataframe"""
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return [
        t["name"], t["company"], t["title"], t["phone"], 
        t["email"], t["address"], t["handwriting_notes"], t["other"]
    ] 