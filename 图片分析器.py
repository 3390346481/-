from PIL import Image
import math
from 配置文件 import Config

class ImageAnalyzer:
    def __init__(self):
        self.min_width = 200
        self.min_height = 150
        self.max_width = 4000
        self.max_height = 4000
    
    def analyze_image(self, image_info):
        image = image_info['content']
        filename = image_info['filename']
        
        width, height = image.size
        is_valid_size = self.min_width <= width <= self.max_width and self.min_height <= height <= self.max_height
        
        has_reasonable_size = width >= self.min_width and height >= self.min_height
        
        aspect_ratio = width / height if height > 0 else 0
        is_reasonable_ratio = 0.25 <= aspect_ratio <= 4.0
        
        format_info = image.format
        
        return {
            'filename': filename,
            'width': width,
            'height': height,
            'format': format_info,
            'is_valid_size': is_valid_size,
            'has_reasonable_size': has_reasonable_size,
            'is_reasonable_ratio': is_reasonable_ratio,
            'aspect_ratio': round(aspect_ratio, 2)
        }
    
    def compare_images(self, student_images, reference_images, threshold=0.8):
        student_count = len(student_images)
        reference_count = len(reference_images)
        
        if reference_count == 0:
            return {
                'match': True,
                'student_count': student_count,
                'reference_count': reference_count,
                'ratio': 1.0 if student_count == 0 else 0.5,
                'missing_count': 0,
                'extra_count': student_count
            }
        
        ratio = student_count / reference_count
        is_match = ratio >= threshold and ratio <= (1 / threshold)
        
        missing_count = max(0, reference_count - student_count)
        extra_count = max(0, student_count - reference_count)
        
        student_analyses = [self.analyze_image(img) for img in student_images]
        reference_analyses = [self.analyze_image(img) for img in reference_images]
        
        return {
            'match': is_match,
            'student_count': student_count,
            'reference_count': reference_count,
            'ratio': round(ratio, 2),
            'missing_count': missing_count,
            'extra_count': extra_count,
            'student_analyses': student_analyses,
            'reference_analyses': reference_analyses
        }
    
    def calculate_image_score(self, comparison_result):
        if comparison_result['reference_count'] == 0:
            return 10
        
        base_score = min(10, comparison_result['ratio'] * 10)
        
        valid_images = sum(1 for img in comparison_result['student_analyses'] if img['is_valid_size'])
        quality_factor = valid_images / max(1, comparison_result['student_count'])
        
        final_score = base_score * quality_factor
        
        return round(final_score, 1)
    
    def count_images_by_section(self, student_report, reference_report):
        result = {}
        
        for section_name in Config.IMAGES_PER_SECTION.keys():
            result[section_name] = {
                'student_count': 0,
                'reference_count': Config.IMAGES_PER_SECTION[section_name]
            }
        
        student_images = student_report.get('images', [])
        reference_images = reference_report.get('images', [])
        
        section_names = list(Config.IMAGES_PER_SECTION.keys())
        
        for i, img in enumerate(student_images):
            if i < len(section_names):
                result[section_names[i]]['student_count'] += 1
        
        return result
