import cv2
import pandas as pd
import numpy as np
import os
import re
from paddleocr import PaddleOCR
from collections import defaultdict
from datetime import datetime


class IntegratedBillProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        self.category_map = self._build_category_map()
        self.symbol_pattern = re.compile(r'[!x]')  # 需要过滤的符号

        # 可调整参数区域
        self.roi_settings = {
            'top': 204,  # 上边界裁剪像素
            'bottom': 95,  # 下边界裁剪像素
            'left': 21,  # 左边界裁剪像素
            'right': 0  # 右边界裁剪像素
        }

        self.color_ranges = {
            'symbol': {  # 特殊符号颜色范围（HSV格式）
                'lower1': [0, 70, 50],
                'upper1': [10, 255, 255],
                'lower2': [170, 70, 50],
                'upper2': [180, 255, 255]
            },
            'green': {  # 金额颜色
                'lower': [35, 50, 50],
                'upper': [85, 255, 255]
            },
            'black': {  # 分类文字颜色
                'lower': [0, 0, 0],
                'upper': [180, 255, 50]
            }
        }

    def _build_category_map(self):
        """构建分类映射字典"""
        return {
            # 保持原有分类结构...
            '买菜': '餐饮', '三餐': '餐饮', '水果': '餐饮', '饮品': '餐饮', '零食': '餐饮',
            '甜品': '餐饮', '粮油调': '餐饮', '日用品': '购物', '衣鞋包': '购物', '护肤美妆': '购物',
            '宠物': '购物', '饰品': '购物', '数码': '购物', '电器': '购物', '软装': '购物',
            '房租': '居家', '水电煤': '居家', '话费': '居家', '网费': '居家', '物业': '居家',
            '维修': '居家', '书籍': '学习', '文物': '学习', '课&卡': '健身', '装备': '健身',
            '日用': '人情', '医药': '人情', '送礼': '人情', '发红包': '人情', '药品': '医疗',
            '保险': '医疗', '保健': '医疗', '治疗': '医疗', '休闲': '娱乐', '请客': '娱乐',
            '约会': '娱乐', '聚会': '娱乐', '公交地铁': '交通', '打车': '交通', '私家车': '交通',
            '飞机火车': '交通', '共享单车': '交通', '年费': '其他', '旅游': '其他',
            '坏账': '其他', '丢失': '其他'
        }

    def process_video(self, video_path, output_excel):
        """主处理流程"""
        cap = cv2.VideoCapture(video_path)
        # 方法 1：直接获取元数据中的帧数（可能不准确）
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames (metadata): {total_frames}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)

        # 跳过前1秒
        #cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps))
        

        monthly_data = defaultdict(list)
        current_month = 12
        frame_counter = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # ROI裁剪
            h, w = frame.shape[:2]
            roi = frame[
                  self.roi_settings['top']:h - self.roi_settings['bottom'],
                  self.roi_settings['left']:w - self.roi_settings['right']
                  ]

            # 月份检测
            month = self._detect_month(roi)
            if month:
                current_month = month
                print(f"检测到新月份: {current_month}")

            # 处理流水记录
            if current_month:
                records = self._process_frame(roi)
                monthly_data[current_month].extend(records)

            frame_counter += 1

        cap.release()
        self._save_to_excel(monthly_data, output_excel)
        return output_excel

    def _detect_month(self, frame):
        """月份横条检测"""
        # 颜色检测+OCR识别
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > frame.shape[1] * 0.8 and h < 50:
                result = self.ocr.ocr(frame[y:y + h, x:x + w], cls=True)
                if result:
                    text = ''.join([line[1][0] for line in result[0]])
                    if '月' in text:
                        return re.sub(r'\D', '', text) + '月'
        return None

    def _process_frame(self, frame):
        """单帧处理流程"""
        # 符号过滤
        symbol_mask = self._create_symbol_mask(frame)

        # 特征提取
        green_mask = self._color_segment(frame, 'green')
        black_mask = self._color_segment(frame, 'black')

        # 合成有效区域
        valid_area = cv2.bitwise_or(green_mask, black_mask)
        clean_area = cv2.bitwise_and(valid_area, cv2.bitwise_not(symbol_mask))

        # OCR处理
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed = cv2.bitwise_and(gray, clean_area)
        result = self.ocr.ocr(processed, cls=True)

        return self._parse_ocr_result(result)

    def _create_symbol_mask(self, frame):
        """创建符号遮罩"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv,
                            np.array(self.color_ranges['symbol']['lower1']),
                            np.array(self.color_ranges['symbol']['upper1']))
        mask2 = cv2.inRange(hsv,
                            np.array(self.color_ranges['symbol']['lower2']),
                            np.array(self.color_ranges['symbol']['upper2']))
        return cv2.bitwise_or(mask1, mask2)

    def _color_segment(self, frame, color_type):
        """颜色分割"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array(self.color_ranges[color_type]['lower'])
        upper = np.array(self.color_ranges[color_type]['upper'])
        return cv2.inRange(hsv, lower, upper)

    def _parse_ocr_result(self, result):
        """解析OCR结果"""
        records = []
        current_date = None

        if not result:
            return records

        for line in result[0]:
            text = self.symbol_pattern.sub('', line[1][0]).strip()
            pos = line[0]
            x_center = (pos[0][0] + pos[2][0]) / 2

            # 日期检测
            if any(c in text for c in ['月', '日']):
                try:
                    date_str = re.search(r'(\d{1,2}月\d{1,2}日)', text).group(1)
                    current_date = datetime.strptime(f'2024{date_str}', '%Y%m月%d日').strftime('%Y-%m-%d')
                    continue
                except:
                    pass

            # 金额检测（右侧70%区域）
            if x_center > 0.7 * (self.roi_settings['right'] - self.roi_settings['left']):
                amount = re.search(r'(\d+\.?\d*)', text.replace('¥', ''))
                if amount and current_date:
                    records[-1]['金额'] = float(amount.group(1))

            # 分类处理
            elif current_date and len(text) > 0:
                parts = text.split()
                if parts:
                    sub_cat = parts[0]
                    main_cat = self.category_map.get(sub_cat, '其他')
                    remark = ' '.join(parts[1:]) if len(parts) > 1 else ''

                    records.append({
                        '日期': current_date,
                        '主分类': main_cat,
                        '子分类': sub_cat,
                        '备注': remark,
                        '金额': 0.0  # 后续由金额检测填充
                    })

        return records

    def _save_to_excel(self, data, output_path):
        """生成Excel文件"""
        with pd.ExcelWriter(output_path) as writer:
            for month in sorted(data.keys(),
                                key=lambda x: int(x[:-1]),
                                reverse=True):
                df = pd.DataFrame(data[month])
                df = df[['日期', '主分类', '子分类', '备注', '金额']]
                df.drop_duplicates(inplace=True)
                df.to_excel(writer, sheet_name=f"{month}月", index=False)


if __name__ == '__main__':
    processor = IntegratedBillProcessor()
    output_file = processor.process_video(
        video_path='2024bill.mp4',
        output_excel='2024年度账单.xlsx'
    )
    print(f"处理完成，结果已保存至：{output_file}")