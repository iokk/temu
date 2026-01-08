"""
TEMU 智能出图系统 V6.6
核心作者: 企鹅

基于 Gemini AI 的电商图片智能生成系统
Zeabur 优化版本
"""
import io
import zipfile
import random
from datetime import date
from PIL import Image
import streamlit as st

from config import Config
from rules import apply_replacements, check_absolute_bans, build_negative_prompt
from gemini_client import GeminiImageClient
from templates import TEMPLATES, TEMPLATE_LABELS
from usage_tracker import UsageTracker


# ============ 页面配置 ============
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)


# ============ 自定义样式 ============
def inject_custom_css():
    """注入自定义 CSS"""
    st.markdown("""
    <style>
    /* 全局优化 */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 渐变标题 */
    h1 {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 按钮样式 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* 文件上传区域 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 0.5rem;
        background: rgba(102, 126, 234, 0.03);
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# ============ 初始化 ============
@st.cache_resource
def get_tracker():
    """获取使用量追踪器（单例）"""
    return UsageTracker()


tracker = get_tracker()


# ============ 认证逻辑 ============
def check_auth() -> bool:
    """检查是否已认证"""
    return st.session_state.get("authenticated", False)


def login_page():
    """登录页面"""
    inject_custom_css()
    
    st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎨 TEMU 智能出图系统</h1>
        <p style="color:#666; font-size: 1.1rem;">AI 驱动的电商图片智能生成平台</p>
        <p style="color:#999;">版本 {Config.APP_VERSION} | 核心作者: {Config.APP_AUTHOR}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能展示
    col1, col2, col3 = st.columns(3)
    features = [
        ("🖼️", "5种专业图片", "主图、场景、细节、对比、规格"),
        ("🤖", "AI 智能分析", "自动识别产品特征和卖点"),
        ("⚡", "快速生成", "一键生成多张专业电商图"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:15px;">
                <div style="font-size:2rem;">{icon}</div>
                <h4 style="margin:0.5rem 0;">{title}</h4>
                <p style="color:#666; font-size:0.85rem; margin:0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 登录表单
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("#### 🔐 请输入访问密码")
            
            password = st.text_input(
                "访问密码", 
                type="password", 
                placeholder="请输入团队密码",
                label_visibility="collapsed"
            )
            
            st.markdown("**API Key 设置** (可选)")
            api_mode = st.radio(
                "选择 API Key 来源",
                [
                    f"🔗 使用团队共享 API（每日 {Config.DAILY_LIMIT} 张）",
                    "🔑 使用个人 API Key（无限额）"
                ],
                index=0,
                label_visibility="collapsed"
            )
            
            user_api_key = ""
            if "个人" in api_mode:
                user_api_key = st.text_input(
                    "你的 Gemini API Key",
                    type="password",
                    placeholder="AIzaSy...",
                    help="在 https://aistudio.google.com/apikey 获取"
                )
            
            submitted = st.form_submit_button("🚀 进入系统", use_container_width=True, type="primary")
            
            if submitted:
                if password == Config.ACCESS_PASSWORD or password == Config.ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = (password == Config.ADMIN_PASSWORD)
                    st.session_state.user_api_key = user_api_key.strip() if user_api_key else None
                    st.session_state.using_own_key = bool(user_api_key.strip())
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 密码错误，请重试")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("💡 没有密码？请联系管理员获取访问权限")
        st.info(f"💡 **小贴士：** {Config.get_random_tip('welcome')}")


def admin_panel():
    """管理员面板"""
    if not st.session_state.get("is_admin"):
        return
        
    st.sidebar.markdown("### 👨‍💼 管理员面板")
    
    if st.sidebar.button("📊 查看统计", use_container_width=True):
        st.session_state.show_stats = not st.session_state.get("show_stats", False)
    
    if st.session_state.get("show_stats"):
        stats = tracker.get_today_stats()
        st.sidebar.metric("📈 今日使用量", f"{stats['total_usage']} 张")
        st.sidebar.metric("👥 活跃用户", f"{stats['active_users']} 人")
        
        if stats['user_details']:
            with st.sidebar.expander("👀 用户明细"):
                for idx, (uid, count) in enumerate(stats['user_details'][:10]):
                    st.text(f"#{idx+1} {uid[:8]}...: {count} 张")
    
    if st.sidebar.button("🗑️ 清空今日数据", use_container_width=True):
        tracker.clear_today_data()
        st.sidebar.success("✅ 已清空")
        st.rerun()


# ============ 主应用 ============
def main_app():
    """主应用界面"""
    inject_custom_css()
    
    # 获取用户信息
    user_id = tracker.get_user_id(st.session_state)
    using_own_key = st.session_state.get("using_own_key", False)
    api_key = st.session_state.get("user_api_key") or Config.GEMINI_API_KEY
    
    # 检查配额
    can_use, remaining = tracker.check_quota(user_id, using_own_key)
    
    # 侧边栏
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding: 0.8rem 0;">
            <h2 style="margin:0;">{Config.PAGE_ICON} TEMU 智能出图</h2>
            <p style="color:#666; margin:0.3rem 0; font-size:0.9rem;">版本 {Config.APP_VERSION}</p>
            <p style="color:#999; font-size:0.8rem;">核心作者: {Config.APP_AUTHOR}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 配额显示
        if using_own_key:
            st.success("🔑 **个人 API Key**\n无限额度")
        else:
            used = Config.DAILY_LIMIT - remaining
            if remaining > 20:
                st.info(f"📊 **今日剩余** {remaining}/{Config.DAILY_LIMIT} 张")
            elif remaining > 0:
                st.warning(f"⚠️ **即将用完** {remaining}/{Config.DAILY_LIMIT} 张")
            else:
                st.error("❌ **今日额度已用完**")
            st.progress(used / Config.DAILY_LIMIT)
        
        st.markdown("---")
        admin_panel()
        
        # 快捷操作
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 刷新", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("🚪 退出", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with st.expander("❓ 帮助"):
            st.markdown("""
            **流程：** 上传图片 → 填写信息 → 选择类型 → 生成 → 下载
            
            **技巧：**
            - 上传高清原图效果更好
            - 风格强度 0.2-0.4 最推荐
            - 可以一次生成多种类型
            """)
    
    # 主界面
    st.markdown("""
    <h1 style="text-align:center;">🎨 TEMU 智能出图系统</h1>
    <p style="text-align:center; color:#666;">AI 驱动的电商图片智能生成</p>
    """, unsafe_allow_html=True)
    
    # 随机提示
    st.markdown(f"""
    <div style="background: linear-gradient(120deg, #667eea15 0%, #764ba215 100%); 
                padding: 0.6rem 1rem; border-radius: 8px; text-align:center; margin-bottom:1rem;">
        💡 {Config.get_random_tip('welcome')}
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化 session state
    if "selected_templates" not in st.session_state:
        st.session_state.selected_templates = []
    if "template_counts" not in st.session_state:
        st.session_state.template_counts = {}
    if "custom_prompts" not in st.session_state:
        st.session_state.custom_prompts = {}
    
    # ============ 第一步：上传图片 ============
    st.markdown("### 📤 第一步：上传商品图片")
    
    uploaded_files = st.file_uploader(
        "选择图片",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        help="支持 PNG、JPG、WebP，建议上传高清原图",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.success(f"✅ 已上传 **{len(uploaded_files)}** 张图片")
        cols = st.columns(min(len(uploaded_files), 5))
        for idx, file in enumerate(uploaded_files[:5]):
            with cols[idx]:
                img = Image.open(file)
                st.image(img, caption=f"图 {idx+1}", use_container_width=True)
        if len(uploaded_files) > 5:
            st.caption(f"还有 {len(uploaded_files) - 5} 张未显示...")
    else:
        st.info("👆 请上传商品图片")
    
    st.divider()
    
    # ============ 第二步：基本信息 ============
    st.markdown("### 📝 第二步：填写商品信息")
    
    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("商品名称 *", placeholder="例如：不锈钢保温杯")
        product_type = st.selectbox(
            "商品类型",
            ["🏠 家居用品", "🍳 厨房用具", "👗 服装配饰", "📱 数码产品", 
             "💄 美妆个护", "🎮 玩具游戏", "⚽ 运动户外", "📦 其他"]
        )
    
    with col2:
        material = st.text_input("材质（可选）", placeholder="例如：304不锈钢")
        size_preset = st.selectbox("输出尺寸", list(Config.SIZE_PRESETS.keys()))
        
        output_size = Config.SIZE_PRESETS[size_preset]
        if size_preset == "自定义":
            c1, c2 = st.columns(2)
            with c1:
                width = st.number_input("宽度", 512, 2048, 1024, 64)
            with c2:
                height = st.number_input("高度", 512, 2048, 1024, 64)
            output_size = (width, height)
    
    st.divider()
    
    # ============ 第三步：选择模板 ============
    st.markdown("### 🎨 第三步：选择图片类型")
    
    template_info = {
        "C1": ("🌟", "主卖点图", "突出核心优势"),
        "C2": ("🏡", "场景图", "展示使用场景"),
        "C3": ("🔍", "细节图", "展现工艺细节"),
        "C4": ("⚖️", "对比图", "对比产品优势"),
        "C5": ("📐", "规格图", "参数信息展示"),
    }
    
    template_cols = st.columns(5)
    for idx, (tid, label) in enumerate(TEMPLATE_LABELS.items()):
        with template_cols[idx]:
            icon, name, desc = template_info.get(tid, ("📷", label, ""))
            st.markdown(f"<div style='text-align:center; font-size:1.5rem;'>{icon}</div>", unsafe_allow_html=True)
            
            if st.checkbox(name, key=f"check_{tid}"):
                if tid not in st.session_state.selected_templates:
                    st.session_state.selected_templates.append(tid)
                    st.session_state.template_counts[tid] = 1
                
                count = st.number_input("数量", 1, 10, st.session_state.template_counts.get(tid, 1), 
                                       key=f"count_{tid}", label_visibility="collapsed")
                st.session_state.template_counts[tid] = count
            else:
                if tid in st.session_state.selected_templates:
                    st.session_state.selected_templates.remove(tid)
                    st.session_state.template_counts.pop(tid, None)
            st.caption(desc)
    
    if not st.session_state.selected_templates:
        st.info("👆 请至少选择一种图片类型")
    else:
        total = sum(st.session_state.template_counts.values())
        st.success(f"✅ 已选 **{len(st.session_state.selected_templates)}** 种类型，共 **{total}** 张")
    
    st.divider()
    
    # ============ 第四步：生成参数 ============
    st.markdown("### ⚙️ 第四步：生成参数")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 AI 模型**")
        model_options = list(Config.AVAILABLE_MODELS.keys())
        default_idx = 0
        for idx, (_, mid) in enumerate(Config.AVAILABLE_MODELS.items()):
            if mid == Config.DEFAULT_MODEL:
                default_idx = idx
                break
        
        selected_model_name = st.selectbox("模型", model_options, index=default_idx, label_visibility="collapsed")
        selected_model = Config.AVAILABLE_MODELS[selected_model_name]
        st.caption(Config.MODEL_DESCRIPTIONS.get(selected_model, ""))
    
    with col2:
        st.markdown("**🎨 风格强度**")
        style_strength = st.slider("强度", Config.STYLE_STRENGTH_MIN, Config.STYLE_STRENGTH_MAX,
                                   Config.DEFAULT_STYLE_STRENGTH, Config.STYLE_STRENGTH_STEP,
                                   label_visibility="collapsed")
        strength_labels = ["🔵 保守", "🟢 推荐", "🟡 平衡", "🟠 创意"]
        st.markdown(strength_labels[min(int(style_strength * 4), 3)])
    
    with col3:
        st.markdown("**🚫 禁用词**")
        exclude_preset = st.selectbox("预设", list(Config.EXCLUDE_PRESETS.keys()), label_visibility="collapsed")
        
        if exclude_preset == "✨ 自定义":
            exclude_items = st.multiselect("选择", Config.COMMON_EXCLUDE_OPTIONS,
                                          default=["competitor logos", "brand names", "watermarks"],
                                          label_visibility="collapsed")
        else:
            exclude_items = Config.EXCLUDE_PRESETS[exclude_preset]
            st.caption(f"包含: {', '.join(exclude_items[:3])}...")
    
    extra_exclude = st.text_input("➕ 额外禁用词（可选）", placeholder="多个词用逗号分隔")
    
    st.divider()
    
    # ============ 生成按钮 ============
    total_images = sum(st.session_state.template_counts.get(t, 1) for t in st.session_state.selected_templates)
    
    if st.session_state.selected_templates:
        col1, col2, col3 = st.columns(3)
        col1.metric("📷 图片数量", f"{total_images} 张")
        col2.metric("🎨 类型数量", f"{len(st.session_state.selected_templates)} 种")
        col3.metric("💰 消耗额度", "0（无限）" if using_own_key else f"{total_images} 张")
    
    if not using_own_key and total_images > remaining:
        st.warning(f"⚠️ 需要 {total_images} 张，剩余 {remaining} 张")
    
    generate_btn = st.button(
        "🚀 开始 AI 智能生成",
        type="primary",
        use_container_width=True,
        disabled=(not can_use and not using_own_key) or not st.session_state.selected_templates
    )
    
    # ============ 生成逻辑 ============
    if generate_btn:
        errors = []
        if not uploaded_files:
            errors.append("请上传至少1张图片")
        if not product_name.strip():
            errors.append("请填写商品名称")
        if not st.session_state.selected_templates:
            errors.append("请选择至少1个图片类型")
        if not using_own_key and total_images > remaining:
            errors.append(f"额度不足")
        
        if errors:
            for e in errors:
                st.error(f"❌ {e}")
            st.stop()
        
        # 清洗输入
        cleaned_name, _ = apply_replacements(product_name)
        cleaned_material, _ = apply_replacements(material)
        
        ban_hits = check_absolute_bans(f"{cleaned_name} {cleaned_material}")
        if ban_hits:
            st.error(f"❌ 检测到禁用内容")
            st.stop()
        
        final_excludes = list(exclude_items)
        if extra_exclude.strip():
            final_excludes.extend([x.strip() for x in extra_exclude.split(",") if x.strip()])
        
        negative_prompt = build_negative_prompt(final_excludes, strict_mode=True)
        
        st.divider()
        
        # AI 分析
        st.markdown("### 🤖 AI 分析中...")
        tip_placeholder = st.empty()
        tip_placeholder.info(Config.get_random_tip("loading"))
        
        client = GeminiImageClient(api_key=api_key, model=selected_model)
        first_image = Image.open(uploaded_files[0]).convert("RGB")
        
        with st.spinner("分析产品特征..."):
            try:
                analysis = client.analyze_product_image(first_image)
                tip_placeholder.success("✅ AI 分析完成！")
                
                with st.expander("📊 AI 分析结果", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**🏷️ 产品**: {analysis.product_description}")
                        st.markdown(f"**🎨 材质**: {analysis.material_guess or '未识别'}")
                    with c2:
                        st.markdown("**✨ 卖点**:")
                        for feat in analysis.key_features[:3]:
                            st.write(f"  • {feat}")
                
                final_material = cleaned_material or analysis.material_guess
                selling_points = "\n".join([f"- {p}" for p in analysis.key_features])
                scene_text = analysis.suggested_scene or "home setting"
                
            except Exception as e:
                tip_placeholder.warning(f"⚠️ AI 分析遇到问题，使用默认参数")
                final_material = cleaned_material
                selling_points = "- Premium quality"
                scene_text = "home setting"
        
        template_vars = {
            "product_name": cleaned_name,
            "product_type": product_type.split(" ")[-1],
            "material": final_material or "high-quality material",
            "selling_points": selling_points,
            "scene": scene_text,
            "detail_focus": "texture and craftsmanship",
            "dimensions": "standard size",
            "compare_points": selling_points,
            "title": cleaned_name.upper()[:30]
        }
        
        st.divider()
        
        # 生成图片
        st.markdown("### 🎨 生成图片中...")
        
        progress = st.progress(0)
        status = st.empty()
        
        results = []
        done = 0
        generated_count = 0
        
        for tid in st.session_state.selected_templates:
            count = st.session_state.template_counts.get(tid, 1)
            prompt_template = st.session_state.custom_prompts.get(tid, TEMPLATES[tid]["default"])
            
            for k in range(count):
                status.info(f"⏳ 生成 **{template_info.get(tid, ('', tid, ''))[1]}** ({k+1}/{count}) - {Config.get_random_tip('loading')}")
                
                try:
                    final_prompt = prompt_template.format(**template_vars)
                    result = client.generate_image_from_reference(
                        reference_image=first_image,
                        prompt=final_prompt,
                        negative_prompt=negative_prompt,
                        style_strength=style_strength
                    )
                    
                    img = result.image.convert("RGB")
                    if output_size:
                        img = img.resize(output_size, Image.Resampling.LANCZOS)
                    
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    filename = f"{tid}_{TEMPLATE_LABELS[tid]}_{k+1}.png"
                    results.append((filename, buf.getvalue(), img))
                    generated_count += 1
                    
                except Exception as e:
                    st.error(f"❌ {tid}-{k+1} 失败: {str(e)[:80]}")
                
                done += 1
                progress.progress(done / total_images)
        
        # 记录使用量
        if generated_count > 0 and not using_own_key:
            tracker.increment_usage(user_id, generated_count)
        
        status.success(Config.get_random_tip("success"))
        
        # 显示结果
        if results:
            st.divider()
            st.markdown("### 🖼️ 生成结果")
            
            cols = st.columns(min(len(results), 4))
            for idx, (filename, _, img) in enumerate(results):
                with cols[idx % 4]:
                    st.image(img, caption=filename, use_container_width=True)
            
            st.divider()
            st.markdown("### 📥 下载")
            
            # 打包 ZIP
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
                for fname, data, _ in results:
                    z.writestr(fname, data)
                
                readme = f"""TEMU 智能出图系统
核心作者: {Config.APP_AUTHOR}
生成时间: {date.today().isoformat()}
商品: {cleaned_name}
数量: {len(results)} 张
"""
                z.writestr("README.txt", readme.encode("utf-8"))
            
            c1, c2 = st.columns([3, 1])
            with c1:
                st.download_button(
                    "⬇️ 下载所有图片 (ZIP)",
                    data=zip_buf.getvalue(),
                    file_name=f"temu_{cleaned_name}_{date.today()}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            with c2:
                new_rem = remaining - generated_count if not using_own_key else "∞"
                st.success(f"✅ 成功 {len(results)} 张\n剩余 {new_rem}")
            
            st.balloons()


# ============ 主入口 ============
def main():
    """主程序入口"""
    config_errors = Config.validate()
    if config_errors:
        st.error("⚠️ **配置错误**")
        for error in config_errors:
            st.error(f"  • {error}")
        st.info("""
        **解决方法：**
        1. 在 Zeabur 控制台设置环境变量 `GEMINI_API_KEY`
        2. 获取 API Key: https://aistudio.google.com/apikey
        """)
        st.stop()
    
    if not check_auth():
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
