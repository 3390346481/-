from 配置文件 import Config

class ScoringEngine:
    def __init__(self):
        self.images_per_section = Config.IMAGES_PER_SECTION
        self.score_per_section = Config.IMAGE_SCORE_PER_SECTION
    
    def score_report(self, section_comparison, image_comparison):
        scores = {}
        total_score = 0
        
        for section_name in self.images_per_section.keys():
            expected_images = self.images_per_section[section_name]
            
            if isinstance(image_comparison, dict) and section_name in image_comparison:
                actual_images = image_comparison[section_name].get('student_count', 0)
            elif isinstance(image_comparison, dict) and 'student_count' in image_comparison:
                actual_images = image_comparison.get('student_count', 0) // len(self.images_per_section)
            else:
                actual_images = 0
            
            if actual_images >= expected_images:
                score = self.score_per_section
            elif actual_images > 0:
                score = round(self.score_per_section * (actual_images / expected_images), 1)
            else:
                score = 0
            
            scores[section_name] = score
            total_score += score
        
        scores['total'] = total_score
        
        return scores
