"""
TEMU 智能出图系统 V8.0
主应用 - 支持 Nano Banana Pro
核心作者: 企鹅

新增功能:
- Nano Banana Pro 模型 (4K, Thinking)
- 多种宽高比选择
- 风格预设
- 重新生成按钮
- 分辨率选择
"""
import io
import zipfile
from datetime import date
from PIL import Image
import streamlit as st

from config import Config
from prompts import PROMPT_TEMPLATES, TEMPLATE_INFO, get_template_names, get_template_prompt
from rules import apply_replacements, check_absolute_bans, build_negative_prompt
from gemini_client import GeminiClient
from usage_tracker import UsageTracker


# ==================== 页面配置 ====================
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)


# ==================== 样式 ====================
def load_css():
    st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; max-width: 1400px; }
    
    h1 { 
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        border: none; border-radius: 10px; font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px); 
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 重新生成按钮 */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #f8f9fa 0%, #fff 100%); 
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea; 
        border-radius: 12px; 
        background: rgba(102, 126, 234, 0.03);
    }
    
    .stProgress > div > div { 
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%); 
    }
    
    /* 卡片样式 */
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-3px);
    }
    
    /* 图片网格 */
    .image-grid img {
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .image-grid img:hover {
        transform: scale(1.02);
    }
    
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ==================== 初始化 ====================
@st.cache_resource
def get_tracker():
    return UsageTracker()

tracker = get_tracker()


# ==================== 认证 ====================
def check_auth() -> bool:
    return st.session_state.get("authenticated", False)


def login_page():
    load_css()
    
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <h1 style="font-size:2.8rem; margin-bottom:0.5rem;">🍌 TEMU 智能出图系统</h1>
        <p style="color:#666; font-size:1.1rem;">Powered by Nano Banana Pro | AI 驱动的电商图片生成</p>
        <p style="color:#999;">版本 V8.0 | 核心作者: 企鹅</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能亮点
    cols = st.columns(4)
    features = [
        ("🍌", "Nano Banana Pro", "专业级生成"),
        ("📸", "4K 超高清", "最高支持4K"),
        ("🎨", "多种风格", "一键切换风格"),
        ("🔄", "智能重生成", "不满意再试"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        col.markdown(f"""
        <div class="feature-card">
            <div style="font-size:2rem">{icon}</div>
            <b>{title}</b><br>
            <small style="color:#666">{desc}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 登录
    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("login"):
            st.markdown("#### 🔐 请输入访问密码")
            password = st.text_input("密码", type="password", label_visibility="collapsed")
            
            st.markdown("**API Key 设置**")
            api_mode = st.radio("来源", [
                f"🔗 团队共享 API（每日 {Config.DAILY_LIMIT} 张）",
                "🔑 个人 API Key（无限额）"
            ], label_visibility="collapsed")
            
            user_key = ""
            if "个人" in api_mode:
                user_key = st.text_input("API Key", type="password", placeholder="AIzaSy...")
            
            if st.form_submit_button("🚀 进入系统", use_container_width=True, type="primary"):
                if password in [Config.ACCESS_PASSWORD, Config.ADMIN_PASSWORD]:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = (password == Config.ADMIN_PASSWORD)
                    st.session_state.user_api_key = user_key.strip() or None
                    st.session_state.using_own_key = bool(user_key.strip())
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 密码错误")
        
        st.info(f"💡 {Config.get_random_tip('welcome')}")


# ==================== 管理面板 ====================
def admin_panel():
    if not st.session_state.get("is_admin"):
        return
    
    st.sidebar.markdown("### 👨‍💼 管理员")
    if st.sidebar.button("📊 统计", use_container_width=True):
        st.session_state.show_stats = not st.session_state.get("show_stats", False)
    
    if st.session_state.get("show_stats"):
        stats = tracker.get_stats()
        st.sidebar.metric("今日使用", f"{stats['total']} 张")
        st.sidebar.metric("活跃用户", f"{stats['users']} 人")
    
    if st.sidebar.button("🗑️ 清空今日", use_container_width=True):
        tracker.clear_today()
        st.rerun()


# ==================== 主应用 ====================
def main_app():
    load_css()
    
    user_id = tracker.get_user_id(st.session_state)
    using_own_key = st.session_state.get("using_own_key", False)
    api_key = st.session_state.get("user_api_key") or Config.get_api_key()
    can_use, remaining = tracker.check_quota(user_id, using_own_key)
    
    # ===== 侧边栏 =====
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:0.5rem;">
            <h2 style="margin:0;">🍌 TEMU 出图</h2>
            <small style="color:#666;">V8.0 | Nano Banana Pro</small>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        if using_own_key:
            st.success("🔑 个人 API\n无限额度")
        else:
            pct = (Config.DAILY_LIMIT - remaining) / Config.DAILY_LIMIT
            st.info(f"📊 剩余 **{remaining}**/{Config.DAILY_LIMIT}")
            st.progress(pct)
        
        st.divider()
        admin_panel()
        
        c1, c2 = st.columns(2)
        if c1.button("🔄 刷新", use_container_width=True):
            st.rerun()
        if c2.button("🚪 退出", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    
    # ===== 主界面 =====
    st.markdown("<h1>🍌 TEMU 智能出图系统</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:#666;'>💡 {Config.get_random_tip('welcome')}</p>", unsafe_allow_html=True)
    
    # 初始化
    for key in ["selected", "counts", "custom_prompts", "generated_results", "last_params"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key in ["selected", "generated_results"] else {}
    
    # ===== 第1步: 上传 =====
    st.markdown("### 📤 第1步: 上传商品图片")
    files = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp"], 
                             accept_multiple_files=True, label_visibility="collapsed")
    
    if files:
        st.success(f"✅ 已上传 {len(files)} 张")
        cols = st.columns(min(len(files), 6))
        for i, f in enumerate(files[:6]):
            cols[i].image(Image.open(f), caption=f"图{i+1}", use_container_width=True)
    
    st.divider()
    
    # ===== 第2步: 基本信息 =====
    st.markdown("### 📝 第2步: 填写商品信息")
    c1, c2 = st.columns(2)
    with c1:
        product_name = st.text_input("商品名称 *", placeholder="例如: 不锈钢保温杯")
        product_type = st.selectbox("类型", ["🏠 家居", "🍳 厨具", "👗 服饰", "📱 数码", "💄 美妆", "🎮 玩具", "📦 其他"])
    with c2:
        material = st.text_input("材质", placeholder="例如: 304不锈钢")
    
    st.divider()
    
    # ===== 第3步: 选择类型 =====
    st.markdown("### 🎨 第3步: 选择图片类型")
    
    template_names = get_template_names()
    cols = st.columns(5)
    
    for i, (tid, name) in enumerate(template_names.items()):
        with cols[i]:
            icon, _, desc = TEMPLATE_INFO.get(tid, ("📷", "", ""))
            st.markdown(f"<div style='text-align:center;font-size:1.8rem'>{icon}</div>", unsafe_allow_html=True)
            
            if st.checkbox(name, key=f"chk_{tid}"):
                if tid not in st.session_state.selected:
                    st.session_state.selected.append(tid)
                    st.session_state.counts[tid] = 1
                st.session_state.counts[tid] = st.number_input(
                    "数量", 1, 5, st.session_state.counts.get(tid, 1), 
                    key=f"cnt_{tid}", label_visibility="collapsed"
                )
            else:
                if tid in st.session_state.selected:
                    st.session_state.selected.remove(tid)
            st.caption(desc)
    
    total = sum(st.session_state.counts.get(t, 0) for t in st.session_state.selected)
    if st.session_state.selected:
        st.success(f"✅ 已选 {len(st.session_state.selected)} 种，共 {total} 张")
    else:
        st.info("👆 请选择至少一种图片类型")
    
    st.divider()
    
    # ===== 第4步: 生成参数 (新增功能!) =====
    st.markdown("### ⚙️ 第4步: 生成参数")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("**🤖 AI 模型**")
        model_name = st.selectbox("模型", list(Config.AVAILABLE_MODELS.keys()), label_visibility="collapsed")
        model_id = Config.AVAILABLE_MODELS[model_name]
        caps = Config.MODEL_CAPABILITIES.get(model_id, {})
        st.caption(Config.MODEL_DESCRIPTIONS.get(model_id, ""))
    
    with c2:
        st.markdown("**📐 宽高比**")
        aspect_name = st.selectbox("比例", list(Config.ASPECT_RATIOS.keys()), label_visibility="collapsed")
        aspect_ratio = Config.ASPECT_RATIOS[aspect_name]
    
    with c3:
        st.markdown("**📺 分辨率**")
        available_res = caps.get("resolutions", ["1K"])
        res_options = {k: v for k, v in Config.RESOLUTIONS.items() if v in available_res}
        if not res_options:
            res_options = {"1K 标准": "1K"}
        res_name = st.selectbox("分辨率", list(res_options.keys()), label_visibility="collapsed")
        resolution = res_options[res_name]
        if resolution in ["2K", "4K"]:
            st.caption(f"✨ {resolution} 高清输出")
    
    with c4:
        st.markdown("**🎨 风格强度**")
        strength = st.slider("强度", 0.0, 1.0, 0.3, 0.1, label_visibility="collapsed")
        labels = ["保守", "推荐", "平衡", "创意"]
        st.caption(labels[min(int(strength * 4), 3)])
    
    # 风格预设
    st.markdown("**✨ 风格预设**")
    c1, c2 = st.columns([1, 2])
    with c1:
        style_preset = st.selectbox("选择风格", list(Config.STYLE_PRESETS.keys()), label_visibility="collapsed")
    with c2:
        if style_preset == "🔧 自定义":
            style_prompt = st.text_input("自定义风格", placeholder="描述你想要的风格...", label_visibility="collapsed")
        else:
            style_prompt = Config.STYLE_PRESETS[style_preset]
            st.caption(f"_{style_prompt[:60]}..._" if len(style_prompt) > 60 else f"_{style_prompt}_")
    
    # 禁用词
    with st.expander("🚫 禁用词设置"):
        preset = st.selectbox("预设", list(Config.EXCLUDE_PRESETS.keys()))
        excludes = Config.EXCLUDE_PRESETS[preset]
        extra = st.text_input("额外禁用词", placeholder="多个用逗号分隔")
    
    st.divider()
    
    # ===== 生成按钮 =====
    c1, c2, c3 = st.columns(3)
    c1.metric("📷 图片数", f"{total} 张")
    c2.metric("📐 比例", aspect_ratio)
    c3.metric("📺 分辨率", resolution)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.button("🚀 开始生成", type="primary", use_container_width=True,
                                disabled=(not can_use and not using_own_key) or not st.session_state.selected)
    with col2:
        regenerate_btn = st.button("🔄 重新生成", use_container_width=True, 
                                  disabled=not st.session_state.get("last_params"))
    
    # ===== 生成逻辑 =====
    should_generate = generate_btn or regenerate_btn
    
    if should_generate:
        # 验证
        if generate_btn:
            errors = []
            if not files:
                errors.append("请上传图片")
            if not product_name.strip():
                errors.append("请填写商品名称")
            if not st.session_state.selected:
                errors.append("请选择图片类型")
            if not using_own_key and total > remaining:
                errors.append("额度不足")
            
            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
                st.stop()
            
            # 保存参数
            st.session_state.last_params = {
                "files": files,
                "product_name": product_name,
                "product_type": product_type,
                "material": material,
                "model_id": model_id,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "strength": strength,
                "style_prompt": style_prompt,
                "excludes": excludes,
                "extra": extra,
                "selected": list(st.session_state.selected),
                "counts": dict(st.session_state.counts),
            }
        
        # 使用保存的参数 (重新生成时)
        params = st.session_state.last_params
        
        # 清洗
        clean_name, _ = apply_replacements(params["product_name"])
        clean_material, _ = apply_replacements(params["material"])
        
        if check_absolute_bans(f"{clean_name} {clean_material}"):
            st.error("❌ 检测到禁用内容")
            st.stop()
        
        final_excludes = list(params["excludes"])
        if params["extra"].strip():
            final_excludes.extend([x.strip() for x in params["extra"].split(",") if x.strip()])
        negative = build_negative_prompt(final_excludes)
        
        st.divider()
        
        # AI 分析
        st.markdown("### 🤖 AI 分析中...")
        tip = st.empty()
        tip.info(Config.get_random_tip("loading"))
        
        client = GeminiClient(api_key, params["model_id"])
        first_img = Image.open(params["files"][0]).convert("RGB")
        
        with st.spinner("分析产品特征..."):
            try:
                analysis = client.analyze_image(first_img)
                tip.success("✅ 分析完成")
                
                with st.expander("📊 AI 分析结果", expanded=True):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**产品**: {analysis.product_description}")
                    c1.markdown(f"**材质**: {analysis.material_guess or '未识别'}")
                    c2.markdown("**卖点**:")
                    for f in analysis.key_features[:3]:
                        c2.write(f"• {f}")
                
                final_material = clean_material or analysis.material_guess
                selling_points = "\n".join([f"- {p}" for p in analysis.key_features])
                scene = analysis.suggested_scene or "home setting"
            except Exception:
                tip.warning("⚠️ 分析失败，使用默认参数")
                final_material = clean_material
                selling_points = "- Premium quality"
                scene = "home setting"
        
        vars = {
            "product_name": clean_name,
            "product_type": params["product_type"].split()[-1],
            "material": final_material or "high-quality material",
            "selling_points": selling_points,
            "scene": scene,
            "detail_focus": "texture and craftsmanship",
            "dimensions": "standard size",
            "title": clean_name.upper()[:30],
            "style_prompt": params["style_prompt"],
        }
        
        st.divider()
        
        # 生成
        st.markdown("### 🎨 生成图片中...")
        
        total_gen = sum(params["counts"].get(t, 1) for t in params["selected"])
        progress = st.progress(0)
        status = st.empty()
        
        results = []
        done = 0
        gen_count = 0
        
        for tid in params["selected"]:
            count = params["counts"].get(tid, 1)
            prompt_tpl = st.session_state.custom_prompts.get(tid) or get_template_prompt(tid)
            _, name, _ = TEMPLATE_INFO.get(tid, ("", tid, ""))
            
            for k in range(count):
                status.info(f"⏳ {name} ({k+1}/{count}) - {Config.get_random_tip('loading')}")
                
                try:
                    prompt = prompt_tpl.format(**vars)
                    result = client.generate_image(
                        reference=first_img,
                        prompt=prompt,
                        negative_prompt=negative,
                        aspect_ratio=params["aspect_ratio"],
                        resolution=params["resolution"],
                        style_strength=params["strength"],
                    )
                    
                    img = result.image.convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    fname = f"{tid}_{name}_{k+1}.png"
                    results.append((fname, buf.getvalue(), img))
                    gen_count += 1
                    
                except Exception as e:
                    st.error(f"❌ {name}-{k+1}: {str(e)[:60]}")
                
                done += 1
                progress.progress(done / total_gen)
        
        if gen_count > 0 and not using_own_key:
            tracker.add_usage(user_id, gen_count)
        
        status.success(Config.get_random_tip("success"))
        st.session_state.generated_results = results
        
        # 显示结果
        if results:
            st.divider()
            st.markdown("### 🖼️ 生成结果")
            
            cols = st.columns(min(len(results), 4))
            for i, (fname, _, img) in enumerate(results):
                with cols[i % 4]:
                    st.image(img, caption=fname, use_container_width=True)
            
            st.divider()
            
            # 下载和重新生成
            st.markdown("### 📥 下载 & 操作")
            
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
                for fname, data, _ in results:
                    z.writestr(fname, data)
                z.writestr("README.txt", f"TEMU智能出图 V8.0\n作者:{Config.APP_AUTHOR}\n日期:{date.today()}\n商品:{clean_name}\n数量:{len(results)}张\n模型:{params['model_id']}\n分辨率:{params['resolution']}".encode())
            
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.download_button("⬇️ 下载全部 (ZIP)", zip_buf.getvalue(),
                                  f"temu_{clean_name}_{date.today()}.zip", "application/zip",
                                  use_container_width=True, type="primary")
            with c2:
                st.success(f"✅ {len(results)}张")
            with c3:
                new_rem = remaining - gen_count if not using_own_key else "∞"
                st.info(f"剩余 {new_rem}")
            
            st.balloons()
    
    # 显示之前的结果
    elif st.session_state.get("generated_results"):
        st.divider()
        st.markdown("### 🖼️ 上次生成结果")
        results = st.session_state.generated_results
        cols = st.columns(min(len(results), 4))
        for i, (fname, _, img) in enumerate(results):
            with cols[i % 4]:
                st.image(img, caption=fname, use_container_width=True)


# ==================== 入口 ====================
def main():
    errors = Config.validate()
    if errors:
        st.error("⚠️ 配置错误")
        for e in errors:
            st.error(f"• {e}")
        st.info("请设置 GEMINI_API_KEY\n获取: https://aistudio.google.com/apikey")
        st.stop()
    
    if not check_auth():
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
