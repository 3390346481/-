import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Levenshtein import ratio as levenshtein_ratio

class ContentComparator:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b[\u4e00-\u9fff]+\b|\b[a-zA-Z]+\b',
            stop_words=None,
            ngram_range=(1, 2)
        )
    
    def preprocess_text(self, text):
        text = text.strip()
        text = re.sub(r'\s+', '', text)
        text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        return text
    
    def calculate_cosine_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        
        text1_clean = self.preprocess_text(text1)
        text2_clean = self.preprocess_text(text2)
        
        if not text1_clean or not text2_clean:
            return 0.0
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1_clean, text2_clean])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return self.calculate_levenshtein_similarity(text1_clean, text2_clean)
    
    def calculate_levenshtein_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        return levenshtein_ratio(text1, text2)
    
    def calculate_jaccard_similarity(self, text1, text2):
        if not text1 or not text2:
            return 0.0
        
        text1_clean = self.preprocess_text(text1)
        text2_clean = self.preprocess_text(text2)
        
        words1 = set(text1_clean)
        words2 = set(text2_clean)
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def calculate_combined_similarity(self, text1, text2):
        cosine_sim = self.calculate_cosine_similarity(text1, text2)
        levenshtein_sim = self.calculate_levenshtein_similarity(text1, text2)
        jaccard_sim = self.calculate_jaccard_similarity(text1, text2)
        
        weights = [0.4, 0.3, 0.3]
        combined = (cosine_sim * weights[0] + levenshtein_sim * weights[1] + jaccard_sim * weights[2])
        
        return round(combined, 3)
    
    def compare_sections(self, student_sections, reference_sections):
        comparison_results = {}
        
        all_sections = set(student_sections.keys()).union(set(reference_sections.keys()))
        
        for section_name in all_sections:
            student_content = student_sections.get(section_name, '')
            reference_content = reference_sections.get(section_name, '')
            
            similarity = self.calculate_combined_similarity(student_content, reference_content)
            
            comparison_results[section_name] = {
                'present_in_student': section_name in student_sections,
                'present_in_reference': section_name in reference_sections,
                'student_content_length': len(student_content),
                'reference_content_length': len(reference_content),
                'similarity': similarity,
                'student_has_content': len(student_content) > 0,
                'reference_has_content': len(reference_content) > 0
            }
        
        return comparison_results
    
    def find_missing_sections(self, comparison_results):
        missing = []
        for section_name, result in comparison_results.items():
            if result['present_in_reference'] and not result['present_in_student']:
                missing.append(section_name)
        return missing
    
    def find_low_similarity_sections(self, comparison_results, threshold=0.6):
        low_sim = []
        for section_name, result in comparison_results.items():
            if result['present_in_reference'] and result['present_in_student']:
                if result['similarity'] < threshold:
                    low_sim.append({
                        'section': section_name,
                        'similarity': result['similarity']
                    })
        return low_sim
    
    def calculate_overall_similarity(self, comparison_results):
        total_weight = 0
        total_score = 0
        
        for section_name, result in comparison_results.items():
            if result['present_in_reference']:
                weight = 1.0
                if result['present_in_student']:
                    total_score += result['similarity'] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_score / total_weight, 3)
    
    def extract_key_terms(self, text, top_n=15):
        text = self.preprocess_text(text)
        if not text:
            return []
        
        try:
            vectorizer = TfidfVectorizer(
                token_pattern=r'(?u)\b[\u4e00-\u9fff]{2,}\b|\b[a-zA-Z]{2,}\b',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            term_score_pairs = list(zip(feature_names, tfidf_scores))
            term_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            return [term for term, score in term_score_pairs[:top_n]]
        except:
            words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{2,}', text)
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:top_n]]
    
    def compare_key_terms(self, student_text, reference_text, top_n=15):
        student_terms = set(self.extract_key_terms(student_text, top_n))
        reference_terms = set(self.extract_key_terms(reference_text, top_n))
        
        common_terms = student_terms.intersection(reference_terms)
        missing_terms = reference_terms - student_terms
        extra_terms = student_terms - reference_terms
        
        return {
            'student_terms': list(student_terms),
            'reference_terms': list(reference_terms),
            'common_terms': list(common_terms),
            'missing_terms': list(missing_terms),
            'extra_terms': list(extra_terms),
            'term_match_ratio': len(common_terms) / max(1, len(reference_terms))
        }
