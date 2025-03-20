import cv2
import pandas as pd
import os
from paddleocr import PaddleOCR

# 分类结构配置
CATEGORIES = {
    '餐饮': ['买菜', '三餐', '水果', '饮品', '零食', '甜品', '粮油调'],
    '购物': ['日用品', '衣鞋包', '护肤美妆', '宠物', '饰品', '数码', '电器', '软装'],
    '居家': ['房租', '水电煤', '话费', '网费', '物业', '维修'],
    '学习': ['书籍', '文具'],
    '健身': ['课&卡', '装备'],
    '人情': ['日用', '医药', '送礼', '发红包'],
    '医疗': ['药品', '保险', '保健', '治疗'],
    '娱乐': ['休闲', '请客', '约会', '聚会'],
    '交通': ['公交地铁', '打车', '私家车', '飞机火车', '共享单车'],
    '其他': ['年费', '旅游', '坏账', '丢失']
}

category_map = {
            '买菜': '餐饮', '三餐': '餐饮', '水果': '餐饮', '饮品': '餐饮', '零食': '餐饮',
            '甜品': '餐饮', '粮油调': '餐饮', '日用品': '购物', '衣鞋包': '购物', '护肤美妆': '购物',
            '宠物': '购物', '饰品': '购物', '数码': '购物', '电器': '购物', '软装': '购物',
            '房租': '居家', '水电煤': '居家', '话费': '居家', '网费': '居家', '物业': '居家',
            '维修': '居家', '书籍': '学习', '文具': '学习', '课&卡': '健身', '装备': '健身',
            '日用': '人情', '医药': '人情', '送礼': '人情', '发红包': '人情', '药品': '医疗',
            '保险': '医疗', '保健': '医疗', '治疗': '医疗', '休闲': '娱乐', '请客': '娱乐',
            '约会': '娱乐', '聚会': '娱乐', '公交地铁': '交通', '打车': '交通', '私家车': '交通',
            '飞机火车': '交通', '共享单车': '交通', '年费': '其他', '旅游': '其他',
            '坏账': '其他', '丢失': '其他'
        }

class VideoBillProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 中文账单请改为 'ch'

    def process_video(self, video_path, output_excel, interval=30, y_threshold=20):
        """处理视频并生成Excel文件"""
        # 创建临时文件夹
        temp_folder = 'temp_frames'
        os.makedirs(temp_folder, exist_ok=True)

        # 提取视频帧
        frame_count = self._extract_frames(video_path, temp_folder, interval)
        
        # 处理所有帧
        all_data = []
        for i in range(frame_count):
            frame_path = os.path.join(temp_folder, f"frame_{i}.jpg")
            processed_data = self._process_frame(frame_path, y_threshold)
            all_data.extend(processed_data)

        # 去重并创建DataFrame
        df = self._create_dataframe(all_data)
        
        # 保存结果
        df.to_excel(output_excel, index=False)
        print(f"成功生成Excel文件：{output_excel}")

        # 清理临时文件
        self._cleanup(temp_folder, frame_count)

    def _extract_frames(self, video_path, output_folder, interval):
        """提取视频帧"""
        vidcap = cv2.VideoCapture(video_path)
        count = 0
        frame_count = 0
        
        while True:
            success, image = vidcap.read()
            if not success:
                break
            
            if count % interval == 0:
                frame_path = os.path.join(output_folder, f"frame_{frame_count}.jpg")
                cv2.imwrite(frame_path, image)
                frame_count += 1
            count += 1
        
        return frame_count

    def _process_frame(self, frame_path, y_threshold):
        """处理单帧图像"""
        # 图像预处理
        image = cv2.imread(frame_path)
        #print('lytest')
        #print(image.size)  # 显示图像像素点个数:1290240
        #print(image.shape) #(960, 448, 3) 图像的高度、宽度以及颜色通道数
        #13.9cm=960,6.5cm=448
        #上面固定2.9cm-（200），下面固定1.35cm-（93），左边去除0.3cm-（20）
        #日期为左边1cm-（20-69），分类为1-3cm（69-207），金额为5-6.5cm（345-448）
        image = image[204:960-95-204, 21:448-21,]  # 截取中间区域
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#用于图像颜色空间转换的函数。它允许你将图像从一个色彩空间转换为另一个色彩空间
        _, processed = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # OCR识别
        result = self.ocr.ocr(processed, cls=True)
        
        # 结构化处理
        texts = [{'text': line[1][0], 'x': line[0][0][0], 'y': line[0][0][1]} 
                for line in result[0]] if result else []
        #print(texts)
        return self._structure_data(texts, y_threshold)

    def _structure_data(self, texts, y_threshold):
        """结构化识别结果"""
        # 按行分组
        sorted_texts = sorted(texts, key=lambda x: x['y'])
        rows = []
        current_row = []
        
        for text in sorted_texts:
            if not current_row or abs(text['y'] - current_row[0]['y']) <= y_threshold:
                current_row.append(text)
            else:
                rows.append(self._create_current_row(current_row))
                current_row = [text]
                
        if current_row:
            rows.append(self._create_current_row(current_row))

        return [[item['text'] for item in row] for row in rows]
    
    def _create_current_row(self, row):
        row = sorted(row, key=lambda x: x['x'])
        secondText = row[0]['text']
        first_text = {'text': ' ', 'x': 20, 'y': 0}
        first_text['y']=row[0]['y']
        #if current_row[0]['x']>40:#如果第一项就是二级分类
        for key in category_map.keys():
            if secondText.find(key) != -1:
                first_text['text'] = category_map[key]
                row[0]['text'] = key
                break

        row.insert(0,first_text)
        return row


    def _create_dataframe(self, data):
        """创建并清理数据"""
        # 去重
        seen = set()
        unique_data = []
        for row in data:
            key = tuple(row)
            if key not in seen and len(row) > 0:
                seen.add(key)
                unique_data.append(row)
        
        # 创建DataFrame
        max_cols = max(len(row) for row in unique_data) if unique_data else 0
        return pd.DataFrame(unique_data, columns=[f'Column_{i+1}' for i in range(max_cols)])

    def _cleanup(self, temp_folder, frame_count):
        """清理临时文件"""
        for i in range(frame_count):
            os.remove(os.path.join(temp_folder, f"frame_{i}.jpg"))
        os.rmdir(temp_folder)

if __name__ == "__main__":
    processor = VideoBillProcessor()
    processor.process_video(
        video_path='2024bill.mp4',  # 替换为你的视频路径
        output_excel='bill_output.xlsx',
        interval=30,      # 每30帧提取一帧（约每秒1帧，假设视频30fps）
        y_threshold=30    # 行高阈值，根据实际情况调整
    )
