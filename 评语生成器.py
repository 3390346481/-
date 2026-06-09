class CommentGenerator:
    def __init__(self):
        self.section_names = {
            '实训目的': '实训目的',
            '实训步骤': '实训步骤',
            '实验结果': '实验结果',
            '问题反思': '问题反思',
            '心得体会': '心得体会'
        }
    
    def generate_positive_comments(self, scores, section_comparison, image_comparison, key_terms_result):
        comments = []
        
        full_score_sections = []
        for section in ['实训目的', '实训步骤', '实验结果', '问题反思', '心得体会']:
            if scores.get(section, 0) >= 18:
                full_score_sections.append(section)
        
        if full_score_sections:
            comments.append(f'{" ".join(full_score_sections)}等章节内容完整。')
        
        if key_terms_result['term_match_ratio'] >= 0.7:
            comments.append(f'报告涵盖了{len(key_terms_result["common_terms"])}个关键知识点，内容全面。')
        
        for section_name, result in section_comparison.items():
            if result['present_in_reference'] and result['present_in_student']:
                if result['similarity'] >= 0.8:
                    comments.append(f'{section_name}部分内容完整，与参考答案高度一致。')
        
        return comments
    
    def generate_improvement_comments(self, scores, section_comparison, image_comparison, key_terms_result, missing_sections, low_sim_sections):
        comments = []
        
        low_score_sections = []
        for section in ['实训目的', '实训步骤', '实验结果', '问题反思', '心得体会']:
            if scores.get(section, 0) < 18:
                low_score_sections.append(section)
        
        if low_score_sections:
            comments.append(f'{" ".join(low_score_sections)}部分图片数量不足，建议补充相关截图或图表。')
        
        if missing_sections:
            comments.append(f'建议补充以下缺失的章节：{" ".join(missing_sections)}。')
        
        if low_sim_sections:
            low_sim = [s['section'] for s in low_sim_sections]
            if low_sim:
                comments.append(f'{" ".join(low_sim)}部分与参考答案差异较大，建议重新核对内容。')
        
        if key_terms_result['missing_terms']:
            missing_terms = key_terms_result['missing_terms'][:5]
            comments.append(f'建议补充以下关键术语：{" ".join(missing_terms)}。')
        
        if image_comparison.get('missing_count', 0) > 0:
            comments.append(f'缺少{image_comparison["missing_count"]}张图片，建议补充相关实验截图或图表。')
        
        return comments
    
    def generate_summary(self, total_score):
        if total_score >= 90:
            return '整体表现优秀，各章节图片完整，内容质量高。'
        elif total_score >= 80:
            return '整体表现良好，部分章节图片需要补充。'
        elif total_score >= 70:
            return '整体表现中等，多个章节需要补充图片。'
        elif total_score >= 60:
            return '整体表现及格，但图片数量不足。'
        else:
            return '整体表现有待提高，建议参考参考答案补充各章节图片。'
    
    def generate_comment(self, scores, section_comparison, image_comparison, key_terms_result, missing_sections, low_sim_sections):
        positive_comments = self.generate_positive_comments(scores, section_comparison, image_comparison, key_terms_result)
        improvement_comments = self.generate_improvement_comments(scores, section_comparison, image_comparison, key_terms_result, missing_sections, low_sim_sections)
        summary = self.generate_summary(scores['total'])
        
        comment_parts = []
        
        if positive_comments:
            comment_parts.append('【优点】')
            comment_parts.extend([f'• {c}' for c in positive_comments])
        
        if improvement_comments:
            comment_parts.append('\n【改进建议】')
            comment_parts.extend([f'• {c}' for c in improvement_comments])
        
        comment_parts.append(f'\n【总体评价】{summary}')
        
        full_comment = '\n'.join(comment_parts)
        
        return full_comment
