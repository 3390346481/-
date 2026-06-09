class Config:
    IMAGES_PER_SECTION = {
        '实训目的': 1,
        '实训步骤': 1,
        '实验结果': 1,
        '问题反思': 1,
        '心得体会': 1
    }
    
    IMAGE_SCORE_PER_SECTION = 20
    
    IMAGE_THRESHOLD = 0.8
    
    SIMILARITY_THRESHOLD = 0.6
    
    SECTION_KEYWORDS = {
        '实训目的': ['实训目的', '实验目的', '学习目标', '教学目标'],
        '实训步骤': ['实训步骤', '实验步骤', '操作步骤', '实现步骤', '开发流程'],
        '实验结果': ['实验结果', '实训结果', '测试结果', '运行结果'],
        '问题反思': ['问题反思', '遇到的问题', '问题分析', '故障排除'],
        '心得体会': ['心得体会', '总结', '收获与体会', '学习感悟']
    }
    
    OUTPUT_FORMATS = ['json', 'html']
    
    BATCH_PROCESS_EXTENSIONS = ['.docx', '.pdf']
