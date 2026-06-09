import streamlit as st
import os
import tempfile
from main import ReportGradingSystem

def main():
    st.set_page_config(
        page_title="实训报告智能批改系统",
        page_icon="📝",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .main-header p {
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
        }
        .upload-box {
            border: 2px dashed #ddd;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        .upload-box:hover {
            border-color: #667eea;
            background-color: #f8f9ff;
        }
        .result-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .score-display {
            font-size: 3rem;
            font-weight: bold;
            color: #4CAF50;
        }
        .section-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        .similarity-bar {
            height: 20px;
            background: #eee;
            border-radius: 10px;
            overflow: hidden;
        }
        .similarity-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.5s ease;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="main-header">
            <h1>📝 实训报告智能批改系统</h1>
            <p>基于图片匹配的智能评分系统，按章节图片数量进行评分</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 上传参考答案")
        reference_file = st.file_uploader("选择参考答案文件", type=None)
        
    with col2:
        st.subheader("📋 上传学生报告")
        student_file = st.file_uploader("选择学生报告文件", type=None)
    
    if st.button("🚀 开始批改", use_container_width=True):
        if not reference_file:
            st.error("请先上传参考答案文件！")
        elif not student_file:
            st.error("请先上传学生报告文件！")
        else:
            with st.spinner("正在分析报告..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    ref_path = os.path.join(tmpdir, reference_file.name)
                    stu_path = os.path.join(tmpdir, student_file.name)
                    
                    with open(ref_path, "wb") as f:
                        f.write(reference_file.getbuffer())
                    with open(stu_path, "wb") as f:
                        f.write(student_file.getbuffer())
                    
                    try:
                        system = ReportGradingSystem()
                        result = system.process_single_report(stu_path, ref_path, os.path.join(tmpdir, "result"), "json")
                        
                        if result:
                            display_results(result, student_file.name)
                        else:
                            st.error("批改过程中出现错误，请检查文件格式是否正确。")
                    except Exception as e:
                        st.error(f"处理过程中发生错误: {str(e)}")

def display_results(result, filename):
    st.markdown("---")
    st.subheader(f"📊 批改结果 - {filename}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="result-card"><div class="score-display">' + str(result['scores']['total']) + '</div><p style="color:#666;">总分（百分制）</p></div>', unsafe_allow_html=True)
        
        st.subheader("各项得分（按章节图片评分）")
        scores = result['scores']
        
        section_items = [
            ("实训目的", scores.get('实训目的', 0), 20),
            ("实训步骤", scores.get('实训步骤', 0), 20),
            ("实验结果", scores.get('实验结果', 0), 20),
            ("问题反思", scores.get('问题反思', 0), 20),
            ("心得体会", scores.get('心得体会', 0), 20)
        ]
        
        for name, score, max_score in section_items:
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            st.markdown(f"""
                <div class="section-card">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-weight: bold;">{name}</span>
                        <span>{score}/{max_score}</span>
                    </div>
                    <div class="similarity-bar">
                        <div class="similarity-fill" style="width: {percentage}%"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("💬 评语")
        if 'comment' in result:
            comment_html = result['comment'].replace('\n', '<br>')
            comment_div = '<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; border-radius: 0 8px 8px 0;">' + comment_html + '</div>'
            st.markdown(comment_div, unsafe_allow_html=True)
        
        st.subheader("📋 章节比对")
        if 'section_comparison' in result:
            for section, data in result['section_comparison'].items():
                if data['present_in_reference']:
                    status = "✓ 已完成" if data['present_in_student'] else "✗ 缺失"
                    color = "#28a745" if data['present_in_student'] else "#dc3545"
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #eee;">
                            <span>{section}</span>
                            <span style="color: {color}; font-weight: bold;">{status}</span>
                        </div>
                    """, unsafe_allow_html=True)
    
    st.subheader("🔍 详细分析")
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**图片分析**")
        if 'image_comparison' in result:
            img_comp = result['image_comparison']
            st.write(f"- 学生报告图片数: {img_comp['student_count']}")
            st.write(f"- 参考答案图片数: {img_comp['reference_count']}")
            st.write(f"- 图片匹配度: {img_comp['ratio'] * 100:.1f}%")
            if img_comp['missing_count'] > 0:
                st.warning(f"缺少 {img_comp['missing_count']} 张图片")
    
    with col4:
        st.markdown("**关键词匹配**")
        if 'key_terms_result' in result:
            terms = result['key_terms_result']
            st.write(f"- 匹配度: {terms['term_match_ratio'] * 100:.1f}%")
            st.write(f"- 共同关键词: {', '.join(terms['common_terms']) if terms['common_terms'] else '无'}")
            if terms['missing_terms']:
                st.warning(f"缺失关键词: {', '.join(terms['missing_terms'][:5])}")

if __name__ == "__main__":
    main()
