import os
import argparse
import sys
from 文档读取器 import DocumentReader
from 图片分析器 import ImageAnalyzer
from 内容比对器 import ContentComparator
from 评分引擎 import ScoringEngine
from 评语生成器 import CommentGenerator
from 报告生成器 import ReportGenerator
from 配置文件 import Config

class ReportGradingSystem:
    def __init__(self):
        self.document_reader = DocumentReader()
        self.image_analyzer = ImageAnalyzer()
        self.content_comparator = ContentComparator()
        self.scoring_engine = ScoringEngine()
        self.comment_generator = CommentGenerator()
        self.report_generator = ReportGenerator()
    
    def load_reference(self, reference_path):
        print(f"正在加载参考答案: {reference_path}")
        return self.document_reader.read_document(reference_path)
    
    def load_student_report(self, report_path):
        print(f"正在读取学生报告: {report_path}")
        return self.document_reader.read_document(report_path)
    
    def grade_report(self, student_report, reference_report):
        print("正在分析章节结构...")
        student_sections = self.document_reader.extract_sections(
            student_report['text'], 
            Config.SECTION_KEYWORDS
        )
        reference_sections = self.document_reader.extract_sections(
            reference_report['text'], 
            Config.SECTION_KEYWORDS
        )
        
        print("正在比对章节内容...")
        section_comparison = self.content_comparator.compare_sections(
            student_sections, 
            reference_sections
        )
        
        print("正在分析图片...")
        image_comparison = self.image_analyzer.compare_images(
            student_report['images'], 
            reference_report['images'],
            Config.IMAGE_THRESHOLD
        )
        image_comparison['score'] = self.image_analyzer.calculate_image_score(image_comparison)
        
        print("正在按章节统计图片...")
        image_by_section = self.image_analyzer.count_images_by_section(student_report, reference_report)
        
        print("正在计算相似度...")
        overall_similarity = self.content_comparator.calculate_overall_similarity(section_comparison)
        
        print("正在比对关键词...")
        key_terms_result = self.content_comparator.compare_key_terms(
            student_report['text'], 
            reference_report['text']
        )
        
        print("正在查找缺失章节...")
        missing_sections = self.content_comparator.find_missing_sections(section_comparison)
        
        print("正在查找低相似度章节...")
        low_sim_sections = self.content_comparator.find_low_similarity_sections(
            section_comparison, 
            Config.SIMILARITY_THRESHOLD
        )
        
        print("正在计算得分...")
        scores = self.scoring_engine.score_report(section_comparison, image_by_section)
        
        print("正在生成评语...")
        comment = self.comment_generator.generate_comment(
            scores,
            section_comparison,
            image_comparison,
            key_terms_result,
            missing_sections,
            low_sim_sections
        )
        
        return {
            'scores': scores,
            'comment': comment,
            'section_comparison': section_comparison,
            'image_comparison': image_comparison,
            'key_terms_result': key_terms_result,
            'missing_sections': missing_sections,
            'low_similarity_sections': low_sim_sections,
            'overall_similarity': overall_similarity
        }
    
    def process_single_report(self, student_path, reference_path, output_path, output_format):
        try:
            reference_report = self.load_reference(reference_path)
            student_report = self.load_student_report(student_path)
            
            grading_result = self.grade_report(student_report, reference_report)
            grading_result['original_filename'] = os.path.basename(student_path)
            
            self.report_generator.generate_report(grading_result, output_path, output_format)
            
            print(f"\n批改完成！")
            print(f"总分: {grading_result['scores']['total']}")
            print(f"输出文件: {output_path}.{output_format}")
            
            return grading_result
            
        except Exception as e:
            print(f"处理报告时出错: {str(e)}")
            return None
    
    def process_batch_reports(self, input_dir, reference_path, output_dir, output_format):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        reference_report = self.load_reference(reference_path)
        
        results = []
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            _, ext = os.path.splitext(filename)
            if ext.lower() not in Config.BATCH_PROCESS_EXTENSIONS:
                continue
            
            print(f"\n处理文件: {filename}")
            
            try:
                student_report = self.load_student_report(file_path)
                grading_result = self.grade_report(student_report, reference_report)
                grading_result['original_filename'] = filename
                
                output_path = os.path.join(output_dir, filename)
                self.report_generator.generate_report(grading_result, output_path, output_format)
                
                print(f"完成！总分: {grading_result['scores']['total']}")
                results.append(grading_result)
                
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")
        
        print(f"\n批量处理完成！共处理 {len(results)} 份报告")
        return results

def main():
    parser = argparse.ArgumentParser(description='实训报告智能批改系统')
    parser.add_argument('--reference', '-r', required=True, help='参考答案文件路径')
    parser.add_argument('--student', '-s', help='学生报告文件路径（单文件模式）')
    parser.add_argument('--input-dir', '-i', help='学生报告文件夹路径（批量模式）')
    parser.add_argument('--output', '-o', help='输出文件路径（单文件模式）')
    parser.add_argument('--output-dir', '-d', help='输出文件夹路径（批量模式）')
    parser.add_argument('--format', '-f', default='html', choices=['json', 'html', 'both'], help='输出格式')
    
    args = parser.parse_args()
    
    if not args.reference:
        print("错误：必须指定参考答案文件路径")
        sys.exit(1)
    
    if not os.path.exists(args.reference):
        print(f"错误：参考答案文件不存在: {args.reference}")
        sys.exit(1)
    
    system = ReportGradingSystem()
    
    if args.student:
        if not os.path.exists(args.student):
            print(f"错误：学生报告文件不存在: {args.student}")
            sys.exit(1)
        
        output_path = args.output if args.output else os.path.splitext(args.student)[0] + '_grading'
        system.process_single_report(args.student, args.reference, output_path, args.format)
    
    elif args.input_dir:
        if not os.path.isdir(args.input_dir):
            print(f"错误：输入文件夹不存在: {args.input_dir}")
            sys.exit(1)
        
        output_dir = args.output_dir if args.output_dir else os.path.join(args.input_dir, 'grading_results')
        system.process_batch_reports(args.input_dir, args.reference, output_dir, args.format)
    
    else:
        print("错误：必须指定学生报告文件(-s)或输入文件夹(-i)")
        sys.exit(1)

if __name__ == '__main__':
    main()
