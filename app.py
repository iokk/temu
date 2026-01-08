"""
TEMU 智能出图系统 V6.5
核心作者: 企鹅

基于 Gemini AI 的电商图片智能生成系统
支持多种电商图片类型（主图、场景图、细节图、对比图、规格图）
"""
import io
import zipfile
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
    layout=Config.LAYOUT
)


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
    st.markdown(f"""
    <div style="text-align:center; padding:50px 20px;">
        <h1>🔐 {Config.APP_NAME}</h1>
        <p style="color:#666;">版本 {Config.APP_VERSION} | 核心作者: {Config.APP_AUTHOR}</p>
        <p style="color:#999; margin-top:20px;">请输入访问密码</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            password = st.text_input(
                "访问密码", 
                type="password", 
                placeholder="请输入团队密码"
            )
            
            st.markdown("---")
            st.markdown("**API Key 设置**（可选）")
            
            api_mode = st.radio(
                "选择 API Key 来源",
                [
                    f"使用团队共享 API（每日 {Config.DAILY_LIMIT} 张额度）",
                    "使用我自己的 API Key（无限额）"
                ],
                index=0
            )
            
            user_api_key = ""
            if "我自己的" in api_mode:
                user_api_key = st.text_input(
                    "你的 Gemini API Key",
                    type="password",
                    placeholder="AIzaSy...",
                    help="在 https://aistudio.google.com/apikey 获取"
                )
            
            submitted = st.form_submit_button("🚀 进入系统", use_container_width=True)
            
            if submitted:
                if password == Config.ACCESS_PASSWORD or password == Config.ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.is_admin = (password == Config.ADMIN_PASSWORD)
                    st.session_state.user_api_key = user_api_key if user_api_key.strip() else None
                    st.session_state.using_own_key = bool(user_api_key.strip())
                    st.rerun()
                else:
                    st.error("❌ 密码错误")
        
        st.markdown("---")
        st.caption("💡 没有密码？请联系管理员获取访问权限")


def admin_panel():
    """管理员面板"""
    if not st.session_state.get("is_admin"):
        return
        
    st.sidebar.markdown("### 👨‍💼 管理员面板")
    
    if st.sidebar.button("📊 查看使用统计"):
        st.session_state.show_stats = True
    
    if st.sidebar.button("🗑️ 清空今日数据"):
        tracker.clear_today_data()
        st.sidebar.success("✅ 已清空今日数据")
        st.rerun()
    
    if st.session_state.get("show_stats"):
        stats = tracker.get_today_stats()
        
        st.sidebar.markdown(f"**今日总使用量**: {stats['total_usage']} 张")
        st.sidebar.markdown(f"**活跃用户数**: {stats['active_users']} 人")
        
        if stats['user_details']:
            st.sidebar.markdown("**用户明细**:")
            for uid, count in stats['user_details'][:10]:  # 显示前10名
                st.sidebar.text(f"  {uid}: {count} 张")


# ============ 主应用 ============
def main_app():
    """主应用界面"""
    # 获取用户信息
    user_id = tracker.get_user_id(st.session_state)
    using_own_key = st.session_state.get("using_own_key", False)
    api_key = st.session_state.get("user_api_key") or Config.GEMINI_API_KEY
    
    # 检查配额
    can_use, remaining = tracker.check_quota(user_id, using_own_key)
    
    # 侧边栏
    with st.sidebar:
        st.markdown(f"## {Config.PAGE_ICON} {Config.APP_NAME}")
        st.caption(f"版本 {Config.APP_VERSION} | 作者: {Config.APP_AUTHOR}")
        
        st.markdown("---")
        
        # 显示配额
        if using_own_key:
            st.success("🔑 使用个人 API Key（无限额）")
        else:
            if remaining > 10:
                st.info(f"📊 今日剩余额度: **{remaining}** 张")
            elif remaining > 0:
                st.warning(f"⚠️ 今日剩余额度: **{remaining}** 张")
            else:
                st.error("❌ 今日额度已用完")
        
        st.markdown("---")
        
        # 管理员面板
        admin_panel()
        
        st.markdown("---")
        
        if st.button("🚪 退出登录", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # 主界面
    st.title(f"{Config.PAGE_ICON} TEMU 智能出图系统")
    st.caption("基于 Gemini AI 的电商图片智能生成")
    
    # 初始化 session state
    if "selected_templates" not in st.session_state:
        st.session_state.selected_templates = []
    if "template_counts" not in st.session_state:
        st.session_state.template_counts = {}
    if "custom_prompts" not in st.session_state:
        st.session_state.custom_prompts = {}
    
    # ============ 第一部分：上传图片 ============
    st.markdown("### 📤 第一步：上传商品图片")
    uploaded_files = st.file_uploader(
        "选择图片",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="上传商品原图，系统将基于原图进行智能优化"
    )
    
    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 5))
        for idx, file in enumerate(uploaded_files[:5]):
            with cols[idx]:
                img = Image.open(file)
                st.image(img, caption=f"图 {idx+1}", use_container_width=True)
        if len(uploaded_files) > 5:
            st.caption(f"已上传 {len(uploaded_files)} 张图片（显示前5张）")
    
    st.divider()
    
    # ============ 第二部分：基本信息 ============
    st.markdown("### 📝 第二步：填写商品信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input(
            "商品名称*",
            placeholder="例如：不锈钢保温杯",
            help="简洁明了的商品名称"
        )
        
        product_type = st.selectbox(
            "商品类型",
            ["家居用品", "厨房用具", "服装配饰", "数码产品", "美妆个护", "玩具游戏", "运动户外", "其他"]
        )
    
    with col2:
        material = st.text_input(
            "材质（可选）",
            placeholder="例如：304不锈钢",
            help="AI 会尝试自动识别，也可以手动指定"
        )
        
        size_preset = st.selectbox(
            "输出尺寸",
            list(Config.SIZE_PRESETS.keys())
        )
        
        output_size = Config.SIZE_PRESETS[size_preset]
        if size_preset == "自定义":
            custom_col1, custom_col2 = st.columns(2)
            with custom_col1:
                width = st.number_input("宽度", 512, 2048, 1024, 64)
            with custom_col2:
                height = st.number_input("高度", 512, 2048, 1024, 64)
            output_size = (width, height)
    
    st.divider()
    
    # ============ 第三部分：选择模板 ============
    st.markdown("### 🎨 第三步：选择图片类型")
    st.caption("可多选，每种类型可生成多张")
    
    template_cols = st.columns(5)
    
    for idx, (tid, label) in enumerate(TEMPLATE_LABELS.items()):
        with template_cols[idx]:
            if st.checkbox(label, key=f"check_{tid}"):
                if tid not in st.session_state.selected_templates:
                    st.session_state.selected_templates.append(tid)
                    st.session_state.template_counts[tid] = 1
                
                count = st.number_input(
                    "数量",
                    1, 10, 
                    st.session_state.template_counts.get(tid, 1),
                    key=f"count_{tid}"
                )
                st.session_state.template_counts[tid] = count
            else:
                if tid in st.session_state.selected_templates:
                    st.session_state.selected_templates.remove(tid)
                    if tid in st.session_state.template_counts:
                        del st.session_state.template_counts[tid]
    
    if not st.session_state.selected_templates:
        st.info("👆 请至少选择一种图片类型")
    else:
        total_count = sum(st.session_state.template_counts.values())
        st.success(f"✅ 已选择 {len(st.session_state.selected_templates)} 种类型，共 {total_count} 张图片")
    
    st.divider()
    
    # ============ 第四部分：提示词配置（可选） ============
    if st.session_state.selected_templates:
        with st.expander("📝 高级：自定义提示词（可选）", expanded=False):
            st.caption("💡 支持变量：{product_name} {material} {selling_points} {scene} {title}")
            
            for tid in st.session_state.selected_templates:
                st.markdown(f"**{tid} - {TEMPLATE_LABELS[tid]}**")
                
                mode = st.radio(
                    "模式",
                    ["使用默认", "自定义"],
                    key=f"mode_{tid}",
                    horizontal=True
                )
                
                if mode == "自定义":
                    current_prompt = st.session_state.custom_prompts.get(
                        tid, 
                        TEMPLATES[tid]["default"]
                    )
                    
                    new_prompt = st.text_area(
                        "编辑提示词",
                        value=current_prompt,
                        height=150,
                        key=f"prompt_{tid}"
                    )
                    st.session_state.custom_prompts[tid] = new_prompt
                    
                    if st.button(f"恢复默认", key=f"reset_{tid}"):
                        st.session_state.custom_prompts[tid] = TEMPLATES[tid]["default"]
                        st.rerun()
                else:
                    st.session_state.custom_prompts[tid] = TEMPLATES[tid]["default"]
                    st.code(TEMPLATES[tid]["default"][:150] + "...", language=None)
                
                st.markdown("---")
    
    st.divider()
    
    # ============ 第五部分：生成参数 ============
    st.markdown("### ⚙️ 第四步：生成参数")
    
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        st.markdown("**🎨 风格强度**")
        style_strength = st.slider(
            "风格强度",
            Config.STYLE_STRENGTH_MIN,
            Config.STYLE_STRENGTH_MAX,
            Config.DEFAULT_STYLE_STRENGTH,
            Config.STYLE_STRENGTH_STEP,
            label_visibility="collapsed"
        )
        
        if style_strength <= 0.2:
            st.caption("🔵 保守 - 高度保留原图")
        elif style_strength <= 0.4:
            st.caption("🟢 推荐 - 保留特征，优化呈现")
        elif style_strength <= 0.6:
            st.caption("🟡 平衡 - 原图与创意各半")
        else:
            st.caption("🟠 创意 - AI 较大发挥空间")
    
    with param_col2:
        st.markdown("**🚫 禁用词预设**")
        exclude_preset = st.selectbox(
            "预设",
            list(Config.EXCLUDE_PRESETS.keys()),
            label_visibility="collapsed"
        )
        
        if exclude_preset == "✨ 自定义":
            exclude_items = st.multiselect(
                "选择禁用项",
                Config.COMMON_EXCLUDE_OPTIONS,
                default=["competitor logos", "brand names", "watermarks"]
            )
        else:
            exclude_items = Config.EXCLUDE_PRESETS[exclude_preset]
            st.caption(f"包含: {', '.join(exclude_items[:3])}...")
    
    extra_exclude = st.text_input(
        "➕ 额外禁用词（可选）",
        placeholder="多个词用逗号分隔"
    )
    
    st.divider()
    
    # ============ 生成按钮 ============
    total_images = sum(st.session_state.template_counts.get(t, 1) 
                      for t in st.session_state.selected_templates)
    
    if not using_own_key and total_images > remaining:
        st.warning(f"⚠️ 计划生成 {total_images} 张，但剩余额度只有 {remaining} 张")
    
    generate_btn = st.button(
        "🚀 开始 AI 智能生成",
        type="primary",
        use_container_width=True,
        disabled=not can_use and not using_own_key
    )
    
    # ============ 生成逻辑 ============
    if generate_btn:
        # 验证输入
        errors = []
        if not uploaded_files:
            errors.append("请上传至少1张图片")
        if not product_name.strip():
            errors.append("请填写商品名称")
        if not st.session_state.selected_templates:
            errors.append("请选择至少1个图片类型")
        if not using_own_key and total_images > remaining:
            errors.append(f"额度不足，需要 {total_images} 张，剩余 {remaining} 张")
        
        if errors:
            for e in errors:
                st.error(f"❌ {e}")
            st.stop()
        
        # 清洗输入
        cleaned_name, _ = apply_replacements(product_name)
        cleaned_material, _ = apply_replacements(material)
        
        # 检查禁用词
        ban_hits = check_absolute_bans(f"{cleaned_name} {cleaned_material}")
        if ban_hits:
            st.error(f"❌ 检测到禁用内容：{', '.join(ban_hits)}")
            st.stop()
        
        # 构建禁用词列表
        final_excludes = list(exclude_items)
        if extra_exclude.strip():
            final_excludes.extend([x.strip() for x in extra_exclude.split(",") if x.strip()])
        
        negative_prompt = build_negative_prompt(final_excludes, strict_mode=True)
        
        st.divider()
        
        # ============ AI 分析 ============
        st.subheader("🤖 AI 分析中...")
        
        client = GeminiImageClient(api_key=api_key, model=Config.IMAGE_MODEL)
        first_image = Image.open(uploaded_files[0]).convert("RGB")
        
        with st.spinner("分析产品特征..."):
            try:
                analysis = client.analyze_product_image(first_image)
                st.success("✅ 分析完成")
                
                with st.expander("📊 AI 分析结果", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**产品**: {analysis.product_description}")
                        st.markdown(f"**材质**: {analysis.material_guess or '未识别'}")
                    with c2:
                        st.markdown("**卖点**:")
                        for feat in analysis.key_features:
                            st.write(f"• {feat}")
                
                final_material = cleaned_material if cleaned_material else analysis.material_guess
                selling_points_text = "\n".join([f"- {p}" for p in analysis.key_features])
                scene_text = analysis.suggested_scene or "home setting"
                
            except Exception as e:
                st.warning(f"⚠️ AI 分析失败: {e}")
                final_material = cleaned_material
                selling_points_text = "- Premium quality"
                scene_text = "home setting"
        
        # 准备模板变量
        template_vars = {
            "product_name": cleaned_name,
            "product_type": product_type,
            "material": final_material or "high-quality material",
            "selling_points": selling_points_text,
            "scene": scene_text,
            "detail_focus": "texture and craftsmanship",
            "dimensions": "standard size",
            "compare_points": selling_points_text,
            "title": cleaned_name.upper()[:30]
        }
        
        st.divider()
        
        # ============ 生成图片 ============
        st.subheader("🎨 生成图片...")
        
        progress = st.progress(0)
        status = st.empty()
        
        results = []
        done = 0
        generated_count = 0
        
        result_container = st.container()
        result_cols = result_container.columns(5)
        
        for tid in st.session_state.selected_templates:
            count = st.session_state.template_counts.get(tid, 1)
            prompt_template = st.session_state.custom_prompts.get(
                tid,
                TEMPLATES[tid]["default"]
            )
            
            for k in range(count):
                status.markdown(f"⏳ 生成 **{tid} - {TEMPLATE_LABELS[tid]}** ({k+1}/{count})")
                
                try:
                    # 格式化提示词
                    final_prompt = prompt_template.format(**template_vars)
                    
                    # 调用 AI 生成
                    result = client.generate_image_from_reference(
                        reference_image=first_image,
                        prompt=final_prompt,
                        negative_prompt=negative_prompt,
                        style_strength=style_strength
                    )
                    
                    # 处理图片
                    img = result.image.convert("RGB")
                    if output_size:
                        img = img.resize(output_size, Image.Resampling.LANCZOS)
                    
                    # 显示缩略图
                    thumb = img.copy()
                    thumb.thumbnail((200, 200))
                    result_cols[done % 5].image(thumb, caption=f"{tid}-{k+1}")
                    
                    # 保存结果
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    filename = f"{tid}_{TEMPLATE_LABELS[tid]}_{k+1}.png"
                    results.append((filename, buf.getvalue()))
                    
                    generated_count += 1
                    done += 1
                    progress.progress(done / total_images)
                    
                except Exception as e:
                    st.error(f"❌ {tid}-{k+1} 生成失败: {str(e)}")
                    done += 1
                    progress.progress(done / total_images)
        
        # 记录使用量
        if generated_count > 0 and not using_own_key:
            tracker.increment_usage(user_id, generated_count)
        
        status.markdown("✅ **生成完成！**")
        
        # ============ 下载 ============
        if results:
            st.divider()
            st.markdown("### 📥 下载生成的图片")
            
            # 打包 ZIP
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
                for fname, data in results:
                    z.writestr(fname, data)
            
            # 添加说明文件
            with zipfile.ZipFile(zip_buf, "a") as z:
                readme = f"""TEMU 智能出图系统生成
                
核心作者: {Config.APP_AUTHOR}
生成时间: {date.today().isoformat()}
商品名称: {cleaned_name}
生成数量: {len(results)} 张

各图片说明：
"""
                for fname, _ in results:
                    readme += f"- {fname}\n"
                
                z.writestr("README.txt", readme.encode("utf-8"))
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.download_button(
                    "⬇️ 打包下载所有图片 (ZIP)",
                    data=zip_buf.getvalue(),
                    file_name=f"temu_{cleaned_name}_{date.today().isoformat()}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            
            with col2:
                # 更新剩余额度显示
                new_remaining = remaining - generated_count if not using_own_key else "∞"
                if using_own_key:
                    st.success(f"✅ 成功 {len(results)} 张")
                else:
                    st.success(f"✅ 剩余 {new_remaining} 张")


# ============ 主入口 ============
def main():
    """主程序入口"""
    # 验证配置
    config_errors = Config.validate()
    if config_errors:
        st.error("⚠️ 配置错误:")
        for error in config_errors:
            st.error(f"- {error}")
        st.stop()
    
    # 认证检查
    if not check_auth():
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
