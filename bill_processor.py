import cv2
import pandas as pd
import os
from paddleocr import PaddleOCR

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
        empty_text = {'text': '', 'x': 50, 'y': 0}
        for text in sorted_texts:
            if not current_row or abs(text['y'] - current_row[0]['y']) <= y_threshold:
                current_row.append(text)
            else:
                current_row = sorted(current_row, key=lambda x: x['x'])
                if current_row[0]['x']>60:
                    empty_text['y']=current_row[0]['y']
                    current_row.insert(0,empty_text)

                rows.append(current_row)

                current_row = [text]
        if current_row:
            rows.append(sorted(current_row, key=lambda x: x['x']))

        return [[item['text'] for item in row] for row in rows]

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
        interval=100,      # 每30帧提取一帧（约每秒1帧，假设视频30fps）
        y_threshold=20    # 行高阈值，根据实际情况调整
    )
