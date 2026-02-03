# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import csv
import os
from datetime import datetime
import re
from collections import defaultdict

class CallAnalyzer:
    def __init__(self):
        self.calls = []
        self.user_phone = ''
    
    def parse_duration(self, duration):
        if not duration:
            return 0
        try:
            return int(float(str(duration)))
        except:
            return 0
    
    def parse_csv(self, content):
        lines = content.split('\n')
        calls = []
        
        header_index = -1
        for i, line in enumerate(lines):
            if '开始时间' in line:
                header_index = i
                break
        
        if header_index == -1:
            print('未找到"开始时间"列')
            return calls
        
        headers = lines[header_index].split(',')
        headers = [h.strip().strip('"') for h in headers]
        
        col_indices = {}
        for idx, h in enumerate(headers):
            h_clean = h.replace(' ', '').replace('　', '')
            if '开始时间' in h_clean:
                col_indices['start_time'] = idx
            elif '事件类型' in h_clean or h_clean == '类型':
                col_indices['type'] = idx
            elif '用户号码' in h_clean:
                col_indices['user_phone'] = idx
            elif '归属地' in h_clean:
                col_indices['user_location'] = idx if '用户' in h else idx
            elif '通话时长' in h_clean and '时长2' not in h_clean:
                col_indices['duration'] = idx
            elif '对端号码' in h_clean or '对方号码' in h_clean:
                col_indices['phone'] = idx
            elif '对端归属地' in h_clean:
                col_indices['phone_location'] = idx
            elif '活动地区' in h_clean:
                col_indices['activity_area'] = idx
            elif 'LAC' in h_clean:
                col_indices['lac'] = idx
            elif '事件状态' in h_clean:
                col_indices['status'] = idx
            elif '通信类型' in h_clean:
                col_indices['comm_type'] = idx
        
        if 'phone' not in col_indices:
            print('未找到电话号码列')
            return calls
        
        data_count = 0
        for i in range(header_index + 1, len(lines)):
            line = lines[i].strip()
            if not line or '合计' in line:
                continue
            
            parts = line.split(',')
            if len(parts) <= max(col_indices.values() if col_indices else [0]):
                continue
            
            try:
                phone_idx = col_indices.get('phone', 5)
                duration_idx = col_indices.get('duration', 4)
                type_idx = col_indices.get('type', 1)
                time_idx = col_indices.get('start_time', 0)
                user_phone_idx = col_indices.get('user_phone', 2)
                user_loc_idx = col_indices.get('user_location', -1)
                phone_loc_idx = col_indices.get('phone_location', -1)
                activity_idx = col_indices.get('activity_area', -1)
                lac_idx = col_indices.get('lac', -1)
                status_idx = col_indices.get('status', -1)
                comm_idx = col_indices.get('comm_type', -1)
                
                phone = str(parts[phone_idx]).strip().strip('"') if phone_idx < len(parts) else ''
                duration = str(parts[duration_idx]).strip().strip('"') if duration_idx < len(parts) else '0'
                call_type = str(parts[type_idx]).strip().strip('"') if type_idx >= 0 and type_idx < len(parts) else ''
                start_time = str(parts[time_idx]).strip().strip('"') if time_idx >= 0 and time_idx < len(parts) else ''
                user_phone = str(parts[user_phone_idx]).strip().strip('"') if user_phone_idx >= 0 and user_phone_idx < len(parts) else ''
                user_location = str(parts[user_loc_idx]).strip().strip('"') if user_loc_idx >= 0 and user_loc_idx < len(parts) else ''
                phone_location = str(parts[phone_loc_idx]).strip().strip('"') if phone_loc_idx >= 0 and phone_loc_idx < len(parts) else ''
                activity_area = str(parts[activity_idx]).strip().strip('"') if activity_idx >= 0 and activity_idx < len(parts) else ''
                lac = str(parts[lac_idx]).strip().strip('"') if lac_idx >= 0 and lac_idx < len(parts) else ''
                status = str(parts[status_idx]).strip().strip('"') if status_idx >= 0 and status_idx < len(parts) else ''
                comm_type = str(parts[comm_idx]).strip().strip('"') if comm_idx >= 0 and comm_idx < len(parts) else ''
                
                phone_clean = re.sub(r'[^\d]', '', phone)
                user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                
                if not phone_clean or len(phone_clean) < 7:
                    continue
                if user_phone_clean and phone_clean == user_phone_clean:
                    continue
                
                calls.append({
                    'type': call_type,
                    'phone': phone,
                    'start_time': start_time,
                    'duration': duration,
                    'duration_sec': self.parse_duration(duration),
                    'user_phone': user_phone,
                    'user_location': user_location,
                    'phone_location': phone_location,
                    'activity_area': activity_area,
                    'lac': lac,
                    'status': status,
                    'comm_type': comm_type
                })
                data_count += 1
            except:
                continue
        
        print(f'CSV解析到 {data_count} 条记录')
        return calls
    
    def parse_xls(self, file_path):
        try:
            import xlrd
            book = xlrd.open_workbook(file_path)
            sheet = book.sheet_by_index(0)
            calls = []
            
            header_row = None
            for i in range(min(10, sheet.nrows)):
                row_values = sheet.row_values(i)
                if '开始时间' in str(row_values):
                    header_row = i
                    break
            
            if header_row is None:
                print('未找到"开始时间"列')
                return calls
            
            headers = sheet.row_values(header_row)
            print(f'XLS列名: {headers[:12]}')
            
            col_indices = {}
            for idx, h in enumerate(headers):
                h_str = str(h).replace(' ', '').replace('　', '')
                if '开始时间' in h_str:
                    col_indices['start_time'] = idx
                elif '事件类型' in h_str or h_str == '类型':
                    col_indices['type'] = idx
                elif '用户号码' in h_str:
                    col_indices['user_phone'] = idx
                elif '归属地' in h_str:
                    col_indices['user_location'] = idx if '用户' in h_str else idx
                elif '通话时长' in h_str and '时长2' not in h_str:
                    col_indices['duration'] = idx
                elif '对端号码' in h_str or '对方号码' in h_str:
                    col_indices['phone'] = idx
                elif '对端归属地' in h_str:
                    col_indices['phone_location'] = idx
                elif '活动地区' in h_str:
                    col_indices['activity_area'] = idx
                elif 'LAC' in h_str:
                    col_indices['lac'] = idx
                elif '事件状态' in h_str:
                    col_indices['status'] = idx
                elif '通信类型' in h_str:
                    col_indices['comm_type'] = idx
            
            if 'phone' not in col_indices:
                print('XLS未找到电话号码列')
                return calls
            
            data_count = 0
            for row_idx in range(header_row + 1, sheet.nrows):
                try:
                    row = sheet.row(row_idx)
                    
                    phone_idx = col_indices.get('phone', 5)
                    duration_idx = col_indices.get('duration', 4)
                    type_idx = col_indices.get('type', 1)
                    time_idx = col_indices.get('start_time', 0)
                    user_phone_idx = col_indices.get('user_phone', 2)
                    user_loc_idx = col_indices.get('user_location', -1)
                    phone_loc_idx = col_indices.get('phone_location', -1)
                    activity_idx = col_indices.get('activity_area', -1)
                    lac_idx = col_indices.get('lac', -1)
                    status_idx = col_indices.get('status', -1)
                    comm_idx = col_indices.get('comm_type', -1)
                    
                    phone = str(row[phone_idx].value).strip() if phone_idx < len(row) else ''
                    duration = str(row[duration_idx].value).strip() if duration_idx < len(row) else '0'
                    call_type = str(row[type_idx].value).strip() if type_idx >= 0 and type_idx < len(row) else ''
                    start_time = str(row[time_idx].value).strip() if time_idx >= 0 and time_idx < len(row) else ''
                    user_phone = str(row[user_phone_idx].value).strip() if user_phone_idx >= 0 and user_phone_idx < len(row) else ''
                    user_location = str(row[user_loc_idx].value).strip() if user_loc_idx >= 0 and user_loc_idx < len(row) else ''
                    phone_location = str(row[phone_loc_idx].value).strip() if phone_loc_idx >= 0 and phone_loc_idx < len(row) else ''
                    activity_area = str(row[activity_idx].value).strip() if activity_idx >= 0 and activity_idx < len(row) else ''
                    lac = str(row[lac_idx].value).strip() if lac_idx >= 0 and lac_idx < len(row) else ''
                    status = str(row[status_idx].value).strip() if status_idx >= 0 and status_idx < len(row) else ''
                    comm_type = str(row[comm_idx].value).strip() if comm_idx >= 0 and comm_idx < len(row) else ''
                    
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                    
                    if not phone_clean or len(phone_clean) < 7:
                        continue
                    if user_phone_clean and phone_clean == user_phone_clean:
                        continue
                    
                    calls.append({
                        'type': call_type,
                        'phone': phone,
                        'start_time': start_time,
                        'duration': duration,
                        'duration_sec': self.parse_duration(duration),
                        'user_phone': user_phone,
                        'user_location': user_location,
                        'phone_location': phone_location,
                        'activity_area': activity_area,
                        'lac': lac,
                        'status': status,
                        'comm_type': comm_type
                    })
                    data_count += 1
                except:
                    continue
            
            print(f'XLS解析到 {data_count} 条记录')
            return calls
        except Exception as e:
            print(f'解析xls失败: {e}')
            return []
    
    def filter_calls(self, phone=None, start_date=None, end_date=None, location=None, min_duration=None):
        """数据筛选和查询"""
        filtered = []
        for c in self.calls:
            # 号码筛选
            if phone and phone not in c['phone']:
                continue
            # 时间筛选
            if start_date or end_date:
                try:
                    call_dt = datetime.strptime(c['start_time'].split(' ')[0], '%Y-%m-%d')
                    if start_date and call_dt < datetime.strptime(start_date, '%Y-%m-%d'):
                        continue
                    if end_date and call_dt > datetime.strptime(end_date, '%Y-%m-%d'):
                        continue
                except:
                    pass
            # 地区筛选
            if location:
                if location not in c.get('phone_location', '') and location not in c.get('activity_area', ''):
                    continue
            # 时长筛选
            if min_duration and c['duration_sec'] < int(min_duration):
                continue
            filtered.append(c)
        return filtered
    
    def get_statistics(self, filtered_calls=None):
        calls = filtered_calls or self.calls
        total_calls = len(calls)
        total_duration = sum(c['duration_sec'] for c in calls)
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        seconds = total_duration % 60
        incoming = len([c for c in calls if '被叫' in c['type']])
        outgoing = len([c for c in calls if '主叫' in c['type']])
        
        # 长时间通话分析
        long_calls = [c for c in calls if c['duration_sec'] >= 300]  # 5分钟以上
        very_long_calls = [c for c in calls if c['duration_sec'] >= 600]  # 10分钟以上
        
        return {
            'total_calls': total_calls,
            'total_duration': f'{hours}小时{minutes}分{seconds}秒',
            'avg_duration': f'{total_duration // total_calls if total_calls > 0 else 0}秒',
            'incoming': incoming,
            'outgoing': outgoing,
            'long_calls_count': len(long_calls),
            'very_long_calls_count': len(very_long_calls),
            'long_calls': long_calls[:50],
            'very_long_calls': very_long_calls[:50]
        }
    
    def get_location_analysis(self):
        """地理信息分析"""
        location_map = defaultdict(lambda: {'count': 0, 'duration': 0, 'phones': set()})
        
        for c in self.calls:
            loc = c.get('phone_location', '') or c.get('activity_area', '')
            if loc:
                location_map[loc]['count'] += 1
                location_map[loc]['duration'] += c['duration_sec']
                location_map[loc]['phones'].add(c['phone'])
        
        locations = []
        for loc, data in location_map.items():
            d = data['duration']
            h = d // 3600
            m = (d % 3600) // 60
            if h > 0:
                dur_str = f'{h}小时{m}分'
            else:
                dur_str = f'{m}分'
            locations.append({
                'location': loc,
                'count': data['count'],
                'duration': dur_str,
                'unique_phones': len(data['phones'])
            })
        
        locations.sort(key=lambda x: x['count'], reverse=True)
        return locations
    
    def get_contact_analysis(self):
        contact_map = {}
        for c in self.calls:
            phone = c['phone']
            if phone not in contact_map:
                contact_map[phone] = {
                    'phone': phone,
                    'count': 0,
                    'total_duration': 0,
                    'last_call': c['start_time'],
                    'locations': set(),
                    'call_types': {'主叫': 0, '被叫': 0}
                }
            contact_map[phone]['count'] += 1
            contact_map[phone]['total_duration'] += c['duration_sec']
            if c['start_time'] > contact_map[phone]['last_call']:
                contact_map[phone]['last_call'] = c['start_time']
            if c.get('phone_location'):
                contact_map[phone]['locations'].add(c['phone_location'])
            if '被叫' in c['type']:
                contact_map[phone]['call_types']['被叫'] += 1
            else:
                contact_map[phone]['call_types']['主叫'] += 1
        
        contacts = []
        for phone, data in contact_map.items():
            d = data['total_duration']
            h = d // 3600
            m = (d % 3600) // 60
            s = d % 60
            if h > 0:
                dur_str = f'{h}小时{m}分{s}秒'
            else:
                dur_str = f'{m}分{s}秒'
            
            contacts.append({
                'phone': phone,
                'count': data['count'],
                'duration': dur_str,
                'last_call': data['last_call'].split(' ')[0] if data['last_call'] else '-',
                'locations': ', '.join(data['locations']) if data['locations'] else '-',
                'call_type': '主叫多' if data['call_types']['主叫'] > data['call_types']['被叫'] else '被叫多'
            })
        
        contacts.sort(key=lambda x: x['count'], reverse=True)
        
        # 跨区域通话分析
        cross_region = [c for c in contacts if ',' in c['locations'] or ('-' not in c['locations'] and len(c['locations']) > 5)]
        
        return {
            'top': contacts[:100],
            'strangers': [c for c in contacts if c['count'] == 1],
            'frequent': [c for c in contacts if c['count'] > 20],
            'cross_region': cross_region[:50]
        }
    
    def get_time_analysis(self, filtered_calls=None):
        calls = filtered_calls or self.calls
        
        hour_dist = [0] * 24
        day_dist = [0] * 7
        month_dist = defaultdict(int)
        weekhour_dist = defaultdict(int)
        days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        
        for c in calls:
            m = re.match(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', c['start_time'])
            if m:
                hour = int(m.group(4))
                month = m.group(1) + '-' + m.group(2)
                date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                hour_dist[hour] += 1
                day_dist[date.weekday()] += 1
                month_dist[month] += 1
                weekhour_dist[f"{days[date.weekday()]}-{hour:02d}"] += 1
        
        night_calls = sum(hour_dist[22:]) + sum(hour_dist[:6])
        morning_calls = sum(hour_dist[6:12])
        afternoon_calls = sum(hour_dist[12:18])
        evening_calls = sum(hour_dist[18:22])
        
        max_count = max(hour_dist) if hour_dist else 0
        peak_hours = [f'{h:02d}:00' for h, c in enumerate(hour_dist) if c == max_count and max_count > 0]
        max_day = max(day_dist) if day_dist else 0
        peak_day = days[day_dist.index(max_day)] if max_day > 0 else '-'
        
        # 月度趋势
        months = sorted(month_dist.keys())
        month_values = [month_dist[m] for m in months]
        
        return {
            'hour_dist': hour_dist,
            'day_dist': day_dist,
            'day_names': days,
            'month_dist': month_dist,
            'months': months,
            'month_values': month_values,
            'weekhour_dist': dict(weekhour_dist),
            'peak_hours': peak_hours,
            'peak_day': peak_day,
            'night_calls': night_calls,
            'night_rate': round(night_calls / len(calls) * 100) if calls else 0,
            'morning_calls': morning_calls,
            'afternoon_calls': afternoon_calls,
            'evening_calls': evening_calls
        }
    
    def get_number_network(self):
        """号码关联分析 - 构建通话网络"""
        network = defaultdict(set)
        for c in self.calls:
            if c['user_phone']:
                network[c['user_phone']].add(c['phone'])
        
        # 找出hub号码（与多个号码有联系）
        hubs = []
        for phone, connections in network.items():
            if len(connections) >= 5:  # 与5个以上不同号码联系
                hubs.append({
                    'phone': phone,
                    'connections': len(connections),
                    'numbers': list(connections)[:10]
                })
        
        hubs.sort(key=lambda x: x['connections'], reverse=True)
        return {'hubs': hubs[:20], 'network_size': len(network)}
    
    def set_user_phone(self, phone):
        self.user_phone = phone
        self.calls = [c for c in self.calls if c['phone'] != phone]

class CallAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('话单分析工具 v1.1')
        self.root.geometry('1200x800')
        self.analyzer = CallAnalyzer()
        self.filtered_calls = None
        self.setup_ui()
    
    def setup_ui(self):
        # 标题
        top_frame = tk.Frame(self.root, bg='#667eea', pady=15)
        top_frame.pack(fill='x')
        tk.Label(top_frame, text='📱 话单分析工具 v1.1', font=('Microsoft YaHei', 20, 'bold'), fg='white', bg='#667eea').pack()
        tk.Label(top_frame, text='支持 CSV、XLS、XLSX 格式 | 数据筛选 | 地理分析 | 号码关联 | 时间趋势', font=('Microsoft YaHei', 10), fg='white', bg='#667eea').pack()
        
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 导入区域
        import_frame = tk.LabelFrame(main_frame, text='📁 导入话单', font=('Microsoft YaHei', 12), padx=15, pady=15)
        import_frame.pack(fill='x', pady=(0, 15))
        
        btn_frame = tk.Frame(import_frame)
        btn_frame.pack()
        tk.Button(btn_frame, text='📂 选择话单文件', font=('Microsoft YaHei', 11), command=self.select_files, bg='#4facfe', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🚀 开始分析', font=('Microsoft YaHei', 11), command=self.start_analysis, bg='#38ef7d', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🔍 筛选查询', font=('Microsoft YaHei', 11), command=self.show_filter_dialog, bg='#f093fb', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🗑️ 清除', font=('Microsoft YaHei', 11), command=self.clear_data, bg='#f5576c', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        
        self.file_label = tk.Label(import_frame, text='支持 CSV、XLS、XLSX 格式，可多选', font=('Microsoft YaHei', 10), fg='#888')
        self.file_label.pack(pady=10)
        
        # 筛选条件显示
        self.filter_label = tk.Label(import_frame, text='当前筛选：无', font=('Microsoft YaHei', 10), fg='#667eea')
        self.filter_label.pack()
        
        # Tab页面
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        self.tab_stats = tk.Frame(self.notebook)
        self.tab_contacts = tk.Frame(self.notebook)
        self.tab_time = tk.Frame(self.notebook)
        self.tab_location = tk.Frame(self.notebook)
        self.tab_network = tk.Frame(self.notebook)
        self.tab_long = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_stats, text='📊 通话统计')
        self.notebook.add(self.tab_contacts, text='👥 联系人分析')
        self.notebook.add(self.tab_time, text='⏰ 时间趋势')
        self.notebook.add(self.tab_location, text='🌍 地理分析')
        self.notebook.add(self.tab_network, text='🔗 号码关联')
        self.notebook.add(self.tab_long, text='📞 长时间通话')
        
        self.setup_stats_tab()
        self.setup_contacts_tab()
        self.setup_time_tab()
        self.setup_location_tab()
        self.setup_network_tab()
        self.setup_long_tab()
    
    def setup_stats_tab(self):
        # 统计卡片
        cards_frame = tk.Frame(self.tab_stats)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        self.stat_cards = []
        colors = ['#667eea', '#11998e', '#f093fb', '#4facfe', '#ff6b6b', '#ffd93d']
        labels = ['总通话次数', '总通话时长', '平均时长', '联系人数', '长时间通话', '熬夜通话']
        for i, (color, label) in enumerate(zip(colors, labels)):
            card = tk.Frame(cards_frame, bg=color, padx=15, pady=12)
            card.grid(row=0, column=i, padx=5, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text='-', font=('Microsoft YaHei', 18, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Microsoft YaHei', 9), fg='white', bg=color).pack()
            self.stat_cards.append(card)
        
        # 通话类型分布
        dist_frame = tk.LabelFrame(self.tab_stats, text='📈 通话类型分布', font=('Microsoft YaHei', 11), padx=15, pady=15)
        dist_frame.pack(fill='x', padx=10, pady=10)
        
        self.type_frame = tk.Frame(dist_frame)
        self.type_frame.pack(fill='x')
        
    def setup_contacts_tab(self):
        sub_notebook = ttk.Notebook(self.tab_contacts)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_freq = tk.Frame(sub_notebook)
        self.tab_cross = tk.Frame(sub_notebook)
        self.tab_frequent = tk.Frame(sub_notebook)
        
        sub_notebook.add(self.tab_freq, text='🔥 通话频次 TOP50')
        sub_notebook.add(self.tab_cross, text='🌐 跨区域联系')
        sub_notebook.add(self.tab_frequent, text='⭐ 高频联系人')
        
        self.create_table(self.tab_freq, ['排名', '号码', '次数', '总时长', '最后通话', '归属地', '主/被叫'], 'freq_table')
        self.create_table(self.tab_cross, ['号码', '次数', '归属地区域'], 'cross_table')
        self.create_table(self.tab_frequent, ['号码', '次数', '总时长'], 'frequent_table')
    
    def setup_time_tab(self):
        # 统计卡片
        cards_frame = tk.Frame(self.tab_time)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        self.time_cards = []
        colors = ['#667eea', '#11998e', '#f093fb', '#4facfe', '#ff6b6b']
        labels = ['高峰时段', '高峰日', '熬夜占比', '上午(6-12)', '下午(12-18)']
        for i, (color, label) in enumerate(zip(colors, labels)):
            card = tk.Frame(cards_frame, bg=color, padx=15, pady=10)
            card.grid(row=0, column=i, padx=3, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text='-', font=('Microsoft YaHei', 14, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Microsoft YaHei', 9), fg='white', bg=color).pack()
            self.time_cards.append(card)
        
        # 小时分布
        hour_frame = tk.LabelFrame(self.tab_time, text='📊 按小时分布（22:00-06:00为熬夜时段）', font=('Microsoft YaHei', 11), padx=15, pady=10)
        hour_frame.pack(fill='x', padx=10, pady=5)
        self.hour_canvas = tk.Canvas(hour_frame, height=150, bg='white')
        self.hour_canvas.pack(fill='x', pady=5)
        
        # 星期分布
        week_frame = tk.LabelFrame(self.tab_time, text='📅 按星期分布', font=('Microsoft YaHei', 11), padx=15, pady=10)
        week_frame.pack(fill='x', padx=10, pady=5)
        self.week_frame = tk.Frame(week_frame)
        self.week_frame.pack(fill='x')
        
        # 月度趋势
        month_frame = tk.LabelFrame(self.tab_time, text='📈 月度通话趋势', font=('Microsoft YaHei', 11), padx=15, pady=10)
        month_frame.pack(fill='x', padx=10, pady=5)
        self.month_canvas = tk.Canvas(month_frame, height=120, bg='white')
        self.month_canvas.pack(fill='x', pady=5)
    
    def setup_location_tab(self):
        cols = ['地区', '通话次数', '总时长', '独立号码数']
        frame = tk.Frame(self.tab_location)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=25)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.location_table = tree
    
    def setup_network_tab(self):
        info_frame = tk.LabelFrame(self.tab_network, text='🔗 号码关联网络', font=('Microsoft YaHei', 11), padx=15, pady=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        self.network_info = tk.Label(info_frame, text='分析中...', font=('Microsoft YaHei', 12), fg='#666')
        self.network_info.pack(anchor='w')
        
        cols = ['号码', '关联号码数', '关联号码列表']
        frame = tk.Frame(self.tab_network)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=20)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.network_table = tree
    
    def setup_long_tab(self):
        cols = ['时间', '号码', '类型', '时长', '归属地']
        frame = tk.Frame(self.tab_long)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=25)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.long_table = tree
        
        tk.Label(self.tab_long, text='* 显示5分钟以上的长时间通话记录', font=('Microsoft YaHei', 10), fg='#888').pack(pady=5)
    
    def create_table(self, parent, columns, var_name):
        frame = tk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        setattr(self, var_name, tree)
    
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[('话单文件', '*.csv *.xls *.xlsx'), ('所有文件', '*.*')])
        if files:
            self.selected_files = files
            self.file_label.config(text=f'已选择 {len(files)} 个文件')
    
    def show_filter_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('数据筛选和查询')
        dialog.geometry('400x300')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text='🔍 数据筛选条件', font=('Microsoft YaHei', 14, 'bold')).pack(pady=15)
        
        # 号码筛选
        tk.Label(dialog, text='号码（包含）:').pack(anchor='w', padx=20)
        phone_entry = tk.Entry(dialog, width=40)
        phone_entry.pack(padx=20, pady=5)
        
        # 时间筛选
        tk.Label(dialog, text='开始日期 (YYYY-MM-DD):').pack(anchor='w', padx=20)
        start_entry = tk.Entry(dialog, width=40)
        start_entry.pack(padx=20, pady=5)
        
        tk.Label(dialog, text='结束日期 (YYYY-MM-DD):').pack(anchor='w', padx=20)
        end_entry = tk.Entry(dialog, width=40)
        end_entry.pack(padx=20, pady=5)
        
        # 地区筛选
        tk.Label(dialog, text='地区（包含）:').pack(anchor='w', padx=20)
        location_entry = tk.Entry(dialog, width=40)
        location_entry.pack(padx=20, pady=5)
        
        # 最小时长
        tk.Label(dialog, text='最短通话时长（秒）:').pack(anchor='w', padx=20)
        duration_entry =        duration_entry = tk.Entry(dialog, width=40)
        duration_entry.pack(padx=20, pady=5)
        
        def apply_filter():
            phone = phone_entry.get().strip()
            start_date = start_entry.get().strip()
            end_date = end_entry.get().strip()
            location = location_entry.get().strip()
            min_duration = duration_entry.get().strip()
            
            self.filter_conditions = {
                'phone': phone if phone else None,
                'start_date': start_date if start_date else None,
                'end_date': end_date if end_date else None,
                'location': location if location else None,
                'min_duration': int(min_duration) if min_duration else None
            }
            
            cond_str = []
            if phone: cond_str.append(f'号码:{phone}')
            if start_date: cond_str.append(f'从{start_date}')
            if end_date: cond_str.append(f'到{end_date}')
            if location: cond_str.append(f'地区:{location}')
            if min_duration: cond_str.append(f'>{min_duration}秒')
            
            self.filter_label.config(text='当前筛选：' + (' | '.join(cond_str) if cond_str else '无'))
            
            if self.analyzer.calls:
                self.filtered_calls = self.analyzer.filter_calls(**self.filter_conditions)
                self.update_all_tabs()
                messagebox.showinfo('完成', f'筛选完成！共 {len(self.filtered_calls)} 条记录')
            
            dialog.destroy()
        
        tk.Button(dialog, text='应用筛选', font=('Microsoft YaHei', 11), command=apply_filter, bg='#667eea', fg='white').pack(pady=20)
        tk.Button(dialog, text='清除筛选', font=('Microsoft YaHei', 11), command=lambda: [setattr(self, 'filter_conditions', None), self.filter_label.config(text='当前筛选：无'), setattr(self, 'filtered_calls', None), dialog.destroy()]).pack(pady=5)
    
    def start_analysis(self):
        if not hasattr(self, 'selected_files') or not self.selected_files:
            messagebox.showwarning('警告', '请先选择话单文件')
            return
        
        self.analyzer.calls = []
        self.filtered_calls = None
        self.filter_conditions = None
        self.filter_label.config(text='当前筛选：无')
        
        for file_path in self.selected_files:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    calls = self.analyzer.parse_csv(content)
                    self.analyzer.calls.extend(calls)
                elif ext == '.xls':
                    calls = self.analyzer.parse_xls(file_path)
                    self.analyzer.calls.extend(calls)
                elif ext == '.xlsx':
                    calls = self.analyzer.parse_xlsx(file_path)
                    self.analyzer.calls.extend(calls)
            except Exception as e:
                print(f'解析失败 {file_path}: {e}')
        
        self.update_all_tabs()
        messagebox.showinfo('完成', f'分析完成！共 {len(self.analyzer.calls)} 条通话记录')
    
    def update_all_tabs(self):
        self.update_stats()
        self.update_contacts()
        self.update_time()
        self.update_location()
        self.update_network()
        self.update_long()
    
    def update_stats(self):
        stats = self.analyzer.get_statistics(self.filtered_calls)
        contacts = self.analyzer.get_contact_analysis()
        
        values = [
            f"{stats['total_calls']} 次",
            stats['total_duration'],
            stats['avg_duration'],
            f"{len(contacts['top'])} 人",
            f"{stats['long_calls_count']} 次",
            f"{stats['night_rate']}%"
        ]
        
        for i, (card, value) in enumerate(zip(self.stat_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    try:
                        int(value.split()[0])
                        child.config(text=value, font=('Microsoft YaHei', 18, 'bold'))
                    except:
                        child.config(text=value, font=('Microsoft YaHei', 12))
        
        # 通话类型分布
        for widget in self.type_frame.winfo_children():
            widget.destroy()
        
        incoming = stats['incoming']
        outgoing = stats['outgoing']
        total = incoming + outgoing
        
        tk.Label(self.type_frame, text=f'主叫: {outgoing} 次 ({round(outgoing/total*100) if total > 0 else 0}%)', font=('Microsoft YaHei', 10), fg='#4facfe').pack(anchor='w', padx=10)
        tk.Label(self.type_frame, text=f'被叫: {incoming} 次 ({round(incoming/total*100) if total > 0 else 0}%)', font=('Microsoft YaHei', 10), fg='#38ef7d').pack(anchor='w', padx=10)
    
    def update_contacts(self):
        contacts = self.analyzer.get_contact_analysis()
        
        for item in self.freq_table.get_children():
            self.freq_table.delete(item)
        for i, c in enumerate(contacts['top'][:50], 1):
            self.freq_table.insert('', 'end', values=[i, c['phone'], f"{c['count']} 次", c['duration'], c['last_call'], c['locations'], c['call_type']])
        
        for item in self.cross_table.get_children():
            self.cross_table.delete(item)
        for c in contacts['cross_region']:
            self.cross_table.insert('', 'end', values=[c['phone'], f"{c['count']} 次", c['locations']])
        
        for item in self.frequent_table.get_children():
            self.frequent_table.delete(item)
        for c in contacts['frequent'][:50]:
            self.frequent_table.insert('', 'end', values=[c['phone'], f"{c['count']} 次", c['duration']])
    
    def update_time(self):
        time_data = self.analyzer.get_time_analysis(self.filtered_calls)
        
        values = [
            ', '.join(time_data['peak_hours']),
            time_data['peak_day'],
            f"{time_data['night_rate']}%",
            f"{time_data['morning_calls']} 次",
            f"{time_data['afternoon_calls']} 次"
        ]
        
        for i, (card, value) in enumerate(zip(self.time_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=value, font=('Microsoft YaHei', 12, 'bold'))
        
        self.root.update()
        
        # 小时柱状图
        self.hour_canvas.delete('all')
        hour_data = time_data['hour_dist']
        max_hour = max(hour_data) if max(hour_data) > 0 else 1
        canvas_width = self.hour_canvas.winfo_width() or 800
        bar_width = max(20, (canvas_width - 100) / 24)
        
        for i, count in enumerate(hour_data):
            height = (count / max_hour) * 120
            x = 50 + i * bar_width
            y = 150 - height
            color = '#667eea' if 8 <= i <= 22 else '#f5576c'
            self.hour_canvas.create_rectangle(x, y, x + bar_width - 2, 150, fill=color, outline='')
            if count > 0:
                self.hour_canvas.create_text(x + bar_width/2, y - 5, text=str(count), font=('Arial', 8))
        
        # 星期柱状图
        for widget in self.week_frame.winfo_children():
            widget.destroy()
        
        day_data = time_data['day_dist']
        days = time_data['day_names']
        max_day = max(day_data) if max(day_data) > 0 else 1
        
        for i, (day, count) in enumerate(zip(days, day_data)):
            frame = tk.Frame(self.week_frame)
            frame.pack(side='left', expand=True, padx=2)
            height = (count / max_day) * 80
            bar = tk.Frame(frame, width=35, height=80, bg='#eee')
            bar.pack()
            bar.pack_propagate(False)
            fill = tk.Frame(bar, width=35, height=int(height), bg='#667eea')
            fill.place(relx=0.5, y=80-int(height), anchor='n')
            tk.Label(frame, text=day, font=('Microsoft YaHei', 9)).pack()
            tk.Label(frame, text=str(count), font=('Microsoft YaHei', 8), fg='#888').pack()
        
        # 月度趋势图
        self.month_canvas.delete('all')
        months = time_data['months']
        month_values = time_data['month_values']
        
        if len(months) > 1:
            max_month = max(month_values) if max(month_values) > 0 else 1
            canvas_width = self.month_canvas.winfo_width() or 800
            bar_width = max(30, (canvas_width - 100) / len(months))
            
            for i, (m, v) in enumerate(zip(months, month_values)):
                height = (v / max_month) * 100
                x = 50 + i * bar_width
                y = 120 - height
                self.month_canvas.create_rectangle(x, y, x + bar_width - 5, 120, fill='#11998e', outline='')
                self.month_canvas.create_text(x + bar_width/2, y - 5, text=f'{v}', font=('Arial', 9))
                self.month_canvas.create_text(x + bar_width/2, 135, text=m, font=('Microsoft YaHei', 8))
    
    def update_location(self):
        locations = self.analyzer.get_location_analysis()
        
        for item in self.location_table.get_children():
            self.location_table.delete(item)
        
        for loc in locations:
            self.location_table.insert('', 'end', values=[loc['location'], f"{loc['count']} 次", loc['duration'], f"{loc['unique_phones']} 个"])
    
    def update_network(self):
        network = self.analyzer.get_number_network()
        
        self.network_info.config(text=f"网络规模：{network['network_size']} 个主号码 | 关联hub数量：{len(network['hubs'])}")
        
        for item in self.network_table.get_children():
            self.network_table.delete(item)
        
        for hub in network['hubs']:
            self.network_table.insert('', 'end', values=[
                hub['phone'],
                f"{hub['connections']} 个",
                ', '.join(hub['numbers'][:5]) + ('...' if len(hub['numbers']) > 5 else '')
            ])
    
    def update_long(self):
        stats = self.analyzer.get_statistics(self.filtered_calls)
        
        for item in self.long_table.get_children():
            self.long_table.delete(item)
        
        for c in stats['long_calls']:
            self.long_table.insert('', 'end', values=[
                c['start_time'],
                c['phone'],
                c['type'],
                c['duration'] + '秒',
                c.get('phone_location', '-')
            ])
    
    def clear_data(self):
        self.analyzer.calls = []
        self.filtered_calls = None
        self.filter_conditions = None
        self.selected_files = []
        self.file_label.config(text='支持 CSV、XLS、XLSX 格式，可多选')
        self.filter_label.config(text='当前筛选：无')
        
        # 清空所有表格
        for item in getattr(self, 'freq_table', tk.Frame()).winfo_children() if hasattr(self, 'freq_table') else []:
            if hasattr(item, 'get_children'):
                for row in item.get_children():
                    item.delete(row)
        
        messagebox.showinfo('完成', '已清除所有数据')

if __name__ == '__main__':
    root = tk.Tk()
    app = CallAnalyzerApp(root)
    root.mainloop()
