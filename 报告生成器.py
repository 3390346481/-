import json
import os
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('.'))
        
    def generate_json_report(self, grading_result, output_path):
        report = {
            'original_filename': grading_result['original_filename'],
            'scores': grading_result['scores'],
            'comment': grading_result['comment'],
            'section_comparison': grading_result['section_comparison'],
            'image_comparison': grading_result['image_comparison'],
            'key_terms_result': grading_result['key_terms_result'],
            'missing_sections': grading_result['missing_sections'],
            'low_similarity_sections': grading_result['low_similarity_sections'],
            'overall_similarity': grading_result['overall_similarity']
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def generate_html_report(self, grading_result, output_path):
        template = self.env.from_string(self.get_html_template())
        
        html_content = template.render(
            original_filename=grading_result['original_filename'],
            scores=grading_result['scores'],
            comment=grading_result['comment'],
            section_comparison=grading_result['section_comparison'],
            image_comparison=grading_result['image_comparison'],
            key_terms_result=grading_result['key_terms_result'],
            missing_sections=grading_result['missing_sections'],
            low_similarity_sections=grading_result['low_similarity_sections'],
            overall_similarity=grading_result['overall_similarity']
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def get_html_template(self):
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>实训报告批改结果 - {{ original_filename }}</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .score-card { display: flex; justify-content: center; margin: 20px 0; }
        .total-score { font-size: 48px; font-weight: bold; color: #4CAF50; text-align: center; }
        .total-label { font-size: 16px; color: #666; }
        .score-section { margin: 20px 0; }
        .score-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .score-item { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .score-name { font-weight: bold; color: #333; }
        .score-value { font-size: 24px; color: #4CAF50; }
        .comment-section { margin: 20px 0; }
        .comment-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 0 8px 8px 0; }
        .section-comparison { margin: 20px 0; }
        .section-item { margin: 10px 0; padding: 10px; border-bottom: 1px solid #eee; }
        .section-name { font-weight: bold; color: #333; }
        .similarity-bar { height: 20px; background: #eee; border-radius: 10px; overflow: hidden; margin: 5px 0; }
        .similarity-fill { height: 100%; background: linear-gradient(90deg, #4CAF50, #8BC34A); }
        .missing-section { color: #dc3545; font-weight: bold; }
        .term-list { list-style: none; padding: 0; }
        .term-item { display: inline-block; background: #e9ecef; padding: 5px 10px; margin: 3px; border-radius: 4px; }
        .key-term-match { color: #28a745; }
        .key-term-missing { color: #dc3545; }
        .image-info { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 8px; }
        .footer { text-align: center; color: #999; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <h1>实训报告智能批改结果</h1>
        
        <div class="score-card">
            <div>
                <div class="total-score">{{ scores.total }}</div>
                <div class="total-label">总分（百分制）</div>
            </div>
        </div>
        
        <div class="score-section">
            <h2>各项得分详情</h2>
            <div class="score-grid">
                <div class="score-item"><div class="score-name">结构完整性 (10分)</div><div class="score-value">{{ scores.structure }}</div></div>
                <div class="score-item"><div class="score-name">关键步骤准确性 (30分)</div><div class="score-value">{{ scores.accuracy }}</div></div>
                <div class="score-item"><div class="score-name">结果匹配度 (25分)</div><div class="score-value">{{ scores.matching }}</div></div>
                <div class="score-item"><div class="score-name">分析深度 (20分)</div><div class="score-value">{{ scores.analysis }}</div></div>
                <div class="score-item"><div class="score-name">图片质量 (10分)</div><div class="score-value">{{ scores.images }}</div></div>
                <div class="score-item"><div class="score-name">格式规范 (5分)</div><div class="score-value">{{ scores.format }}</div></div>
            </div>
        </div>
        
        <div class="comment-section">
            <h2>评语</h2>
            <div class="comment-box">{{ comment.replace('\n', '<br>')|safe }}</div>
        </div>
        
        <div class="section-comparison">
            <h2>章节比对结果</h2>
            {% for section_name, result in section_comparison.items() %}
            <div class="section-item">
                <div class="section-name">{{ section_name }}</div>
                <div>
                    {% if result.present_in_student and result.present_in_reference %}
                    <div>相似度: {{ (result.similarity * 100)|round(1) }}%</div>
                    <div class="similarity-bar"><div class="similarity-fill" style="width: {{ result.similarity * 100 }}%"></div></div>
                    {% elif result.present_in_reference and not result.present_in_student %}
                    <div class="missing-section">✗ 缺失</div>
                    {% else %}
                    <div>仅学生报告中有此章节</div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div>
            <h2>图片分析</h2>
            <div class="image-info">
                <div>学生报告图片数: {{ image_comparison.student_count }}</div>
                <div>参考答案图片数: {{ image_comparison.reference_count }}</div>
                <div>图片匹配度: {{ (image_comparison.ratio * 100)|round(1) }}%</div>
                {% if image_comparison.missing_count > 0 %}
                <div class="missing-section">缺少图片: {{ image_comparison.missing_count }} 张</div>
                {% endif %}
            </div>
        </div>
        
        <div>
            <h2>关键词匹配</h2>
            <div>匹配度: {{ (key_terms_result.term_match_ratio * 100)|round(1) }}%</div>
            <div>
                <h4>共同关键词:</h4>
                <ul class="term-list">
                {% for term in key_terms_result.common_terms %}
                    <li class="term-item key-term-match">{{ term }}</li>
                {% endfor %}
                </ul>
            </div>
            {% if key_terms_result.missing_terms %}
            <div>
                <h4>缺失关键词:</h4>
                <ul class="term-list">
                {% for term in key_terms_result.missing_terms %}
                    <li class="term-item key-term-missing">{{ term }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        {% if low_similarity_sections %}
        <div>
            <h2>低相似度章节</h2>
            <ul>
            {% for item in low_similarity_sections %}
                <li>{{ item.section }} - 相似度: {{ (item.similarity * 100)|round(1) }}%</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>实训报告智能批改系统</p>
        </div>
    </div>
</body>
</html>
        """
    
    def generate_report(self, grading_result, output_path, format='json'):
        base_name = os.path.splitext(output_path)[0]
        
        if format == 'json':
            self.generate_json_report(grading_result, f'{base_name}.json')
        elif format == 'html':
            self.generate_html_report(grading_result, f'{base_name}.html')
        else:
            self.generate_json_report(grading_result, f'{base_name}.json')
            self.generate_html_report(grading_result, f'{base_name}.html')
