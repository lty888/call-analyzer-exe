# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from datetime import datetime
import re
from collections import defaultdict

class CallAnalyzer:
    def __init__(self):
        self.calls = []
        self.user_phone = ''
        self.last_error = ''
    
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
        self.last_error = ''
        
        header_index = -1
        for i, line in enumerate(lines):
            if '开始时间' in line:
                header_index = i
                break
        
        if header_index == -1:
            self.last_error = '未找到"开始时间"列，请检查话单格式'
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
            elif '通话时长' in h_clean and '时长2' not in h_clean:
                col_indices['duration'] = idx
            elif '对端号码' in h_clean or '对方号码' in h_clean:
                col_indices['phone'] = idx
            elif '对端归属地' in h_clean:
                col_indices['phone_location'] = idx
            elif '活动地区' in h_clean:
                col_indices['activity_area'] = idx
        
        if 'phone' not in col_indices:
            self.last_error = '未找到电话号码列，请检查话单格式'
            return calls
        
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
                phone_loc_idx = col_indices.get('phone_location', -1)
                activity_idx = col_indices.get('activity_area', -1)
                
                phone = str(parts[phone_idx]).strip().strip('"') if phone_idx < len(parts) else ''
                duration = str(parts[duration_idx]).strip().strip('"') if duration_idx < len(parts) else '0'
                call_type = str(parts[type_idx]).strip().strip('"') if type_idx >= 0 and type_idx < len(parts) else ''
                start_time = str(parts[time_idx]).strip().strip('"') if time_idx >= 0 and time_idx < len(parts) else ''
                user_phone = str(parts[user_phone_idx]).strip().strip('"') if user_phone_idx >= 0 and user_phone_idx < len(parts) else ''
                phone_location = str(parts[phone_loc_idx]).strip().strip('"') if phone_loc_idx >= 0 and phone_loc_idx < len(parts) else ''
                activity_area = str(parts[activity_idx]).strip().strip('"') if activity_idx >= 0 and activity_idx < len(parts) else ''
                
                phone_clean = re.sub(r'[^\d]', '', phone)
                user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                
                if not phone_clean or len(phone_clean) < 7:
                    continue
                if user_phone_clean and phone_clean == user_phone_clean:
                    continue
                
                calls.append({
                    'type': call_type, 'phone': phone, 'start_time': start_time,
                    'duration': duration, 'duration_sec': self.parse_duration(duration),
                    'user_phone': user_phone, 'phone_location': phone_location,
                    'activity_area': activity_area
                })
            except:
                continue
        
        return calls
    
    def parse_xls(self, file_path):
        try:
            import xlrd
            book = xlrd.open_workbook(file_path)
            sheet = book.sheet_by_index(0)
            calls = []
            self.last_error = ''
            
            header_row = None
            for i in range(min(10, sheet.nrows)):
                row_values = sheet.row_values(i)
                if '开始时间' in str(row_values):
                    header_row = i
                    break
            
            if header_row is None:
                self.last_error = '未找到"开始时间"列'
                return calls
            
            headers = sheet.row_values(header_row)
            
            col_indices = {}
            for idx, h in enumerate(headers):
                h_str = str(h).replace(' ', '').replace('　', '')
                if '开始时间' in h_str:
                    col_indices['start_time'] = idx
                elif '事件类型' in h_str or h_str == '类型':
                    col_indices['type'] = idx
                elif '用户号码' in h_str:
                    col_indices['user_phone'] = idx
                elif '通话时长' in h_str and '时长2' not in h_str:
                    col_indices['duration'] = idx
                elif '对端号码' in h_str or '对方号码' in h_str:
                    col_indices['phone'] = idx
                elif '对端归属地' in h_str:
                    col_indices['phone_location'] = idx
                elif '活动地区' in h_str:
                    col_indices['activity_area'] = idx
            
            if 'phone' not in col_indices:
                self.last_error = '未找到电话号码列'
                return calls
            
            for row_idx in range(header_row + 1, sheet.nrows):
                try:
                    row = sheet.row(row_idx)
                    
                    phone = str(row[col_indices.get('phone', 5)].value).strip() if col_indices.get('phone', 5) < len(row) else ''
                    duration = str(row[col_indices.get('duration', 4)].value).strip() if col_indices.get('duration', 4) < len(row) else '0'
                    call_type = str(row[col_indices.get('type', 1)].value).strip() if col_indices.get('type', 1) < len(row) else ''
                    start_time = str(row[col_indices.get('start_time', 0)].value).strip() if col_indices.get('start_time', 0) < len(row) else ''
                    user_phone = str(row[col_indices.get('user_phone', 2)].value).strip() if col_indices.get('user_phone', 2) < len(row) else ''
                    phone_location = str(row[col_indices.get('phone_location', -1)].value).strip() if col_indices.get('phone_location', -1) >= 0 and col_indices.get('phone_location', -1) < len(row) else ''
                    activity_area = str(row[col_indices.get('activity_area', -1)].value).strip() if col_indices.get('activity_area', -1) >= 0 and col_indices.get('activity_area', -1) < len(row) else ''
                    
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                    
                    if not phone_clean or len(phone_clean) < 7:
                        continue
                    if user_phone_clean and phone_clean == user_phone_clean:
                        continue
                    
                    calls.append({
                        'type': call_type, 'phone': phone, 'start_time': start_time,
                        'duration': duration, 'duration_sec': self.parse_duration(duration),
                        'user_phone': user_phone, 'phone_location': phone_location,
                        'activity_area': activity_area
                    })
                except:
                    continue
            
            return calls
        except Exception as e:
            self.last_error = f'解析XLS失败: {str(e)}'
            return []
    
    def parse_xlsx(self, file_path):
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            calls = []
            self.last_error = ''
            
            for _, row in df.iterrows():
                try:
                    phone = str(row.get('对端号码', row.get('对方号码', ''))).strip()
                    if not phone:
                        continue
                    
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    if len(phone_clean) < 7:
                        continue
                    
                    user_phone = str(row.get('用户号码', '')).strip()
                    user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                    if user_phone_clean and phone_clean == user_phone_clean:
                        continue
                    
                    duration = str(row.get('通话时长', '0'))
                    calls.append({
                        'type': str(row.get('事件类型', row.get('类型', ''))).strip(),
                        'phone': phone, 'start_time': str(row.get('开始时间', '')).strip(),
                        'duration': duration, 'duration_sec': self.parse_duration(duration),
                        'user_phone': user_phone,
                        'phone_location': str(row.get('对端归属地', '')).strip(),
                        'activity_area': str(row.get('活动地区', '')).strip()
                    })
                except:
                    continue
            
            return calls
        except Exception as e:
            self.last_error = f'解析XLSX失败: {str(e)}'
            return []
    
    def filter_calls(self, phone=None, start_date=None, end_date=None, location=None):
        filtered = []
        for c in self.calls:
            if phone and phone not in c['phone']:
                continue
            if start_date or end_date:
                try:
                    call_dt = datetime.strptime(c['start_time'].split(' ')[0], '%Y-%m-%d')
                    if start_date and call_dt < datetime.strptime(start_date, '%Y-%m-%d'):
                        continue
                    if end_date and call_dt > datetime.strptime(end_date, '%Y-%m-%d'):
                        continue
                except:
                    pass
            if location:
                if location not in c.get('phone_location', '') and location not in c.get('activity_area', ''):
                    continue
            filtered.append(c)
        return filtered
    
    def get_statistics(self, filtered_calls=None):
        calls = filtered_calls or self.calls
        total_calls = len(calls)
        total_duration = sum(c['duration_sec'] for c in calls)
        h, m, s = total_duration // 3600, (total_duration % 3600) // 60, total_duration % 60
        incoming = len([c for c in calls if '被叫' in c['type']])
        outgoing = len([c for c in calls if '主叫' in c['type']])
        long_calls = [c for c in calls if c['duration_sec'] >= 300]
        
        return {
            'total_calls': total_calls, 'total_duration': f'{h}小时{m}分{s}秒',
            'avg_duration': f'{total_duration // total_calls if total_calls > 0 else 0}秒',
            'incoming': incoming, 'outgoing': outgoing,
            'long_calls_count': len(long_calls), 'long_calls': long_calls[:50]
        }
    
    def get_contact_analysis(self):
        contact_map = {}
        for c in self.calls:
            phone = c['phone']
            if phone not in contact_map:
                contact_map[phone] = {'phone': phone, 'count': 0, 'total_duration': 0,
                    'last_call': c['start_time'], 'locations': set()}
            contact_map[phone]['count'] += 1
            contact_map[phone]['total_duration'] += c['duration_sec']
            if c['start_time'] > contact_map[phone]['last_call']:
                contact_map[phone]['last_call'] = c['start_time']
            if c.get('phone_location'):
                contact_map[phone]['locations'].add(c['phone_location'])
        
        contacts = []
        for phone, data in contact_map.items():
            d = data['total_duration']
            h, m, s = d // 3600, (d % 3600) // 60, d % 60
            dur_str = f'{h}小时{m}分{s}秒' if h > 0 else f'{m}分{s}秒'
            contacts.append({
                'phone': phone, 'count': data['count'], 'duration': dur_str,
                'last_call': data['last_call'].split(' ')[0] if data['last_call'] else '-',
                'locations': ', '.join(data['locations']) if data['locations'] else '-'
            })
        contacts.sort(key=lambda x: x['count'], reverse=True)
        return {'top': contacts[:100], 'strangers': [c for c in contacts if c['count'] == 1], 'frequent': [c for c in contacts if c['count'] > 20]}
    
    def get_time_analysis(self, filtered_calls=None):
        calls = filtered_calls or self.calls
        hour_dist = [0] * 24
        day_dist = [0] * 7
        days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        
        for c in calls:
            m = re.match(r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', c['start_time'])
            if m:
                hour = int(m.group(4))
                date = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                hour_dist[hour] += 1
                day_dist[date.weekday()] += 1
        
        night_calls = sum(hour_dist[22:]) + sum(hour_dist[:6])
        max_count = max(hour_dist) if hour_dist else 0
        peak_hours = [f'{h:02d}:00' for h, c in enumerate(hour_dist) if c == max_count and max_count > 0]
        max_day = max(day_dist) if day_dist else 0
        peak_day = days[day_dist.index(max_day)] if max_day > 0 else '-'
        
        return {
            'hour_dist': hour_dist, 'day_dist': day_dist, 'day_names': days,
            'peak_hours': peak_hours, 'peak_day': peak_day,
            'night_calls': night_calls, 'night_rate': round(night_calls / len(calls) * 100) if calls else 0,
            'morning_calls': sum(hour_dist[6:12]), 'afternoon_calls': sum(hour_dist[12:18])
        }
    
    def get_location_analysis(self):
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
            h, m = d // 3600, (d % 3600) // 60
            locations.append({
                'location': loc, 'count': data['count'],
                'duration': f'{h}小时{m}分' if h > 0 else f'{m}分',
                'unique_phones': len(data['phones'])
            })
        locations.sort(key=lambda x: x['count'], reverse=True)
        return locations
    
    def get_number_network(self):
        network = defaultdict(set)
        for c in self.calls:
            if c['user_phone']:
                network[c['user_phone']].add(c['phone'])
        hubs = [{'phone': p, 'connections': len(connections), 'numbers': list(connections)[:10]} 
                for p, connections in network.items() if len(connections) >= 5]
        hubs.sort(key=lambda x: x['connections'], reverse=True)
        return {'hubs': hubs[:20], 'network_size': len(network)}

class CallAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('话单分析工具 v1.1')
        self.root.geometry('1200x800')
        self.analyzer = CallAnalyzer()
        self.filtered_calls = None
        self.setup_ui()
    
    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg='#667eea', pady=15)
        top_frame.pack(fill='x')
        tk.Label(top_frame, text='📱 话单分析工具 v1.1', font=('Microsoft YaHei', 20, 'bold'), fg='white', bg='#667eea').pack()
        tk.Label(top_frame, text='支持 CSV、XLS、XLSX 格式', font=('Microsoft YaHei', 10), fg='white', bg='#667eea').pack()
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        import_frame = tk.LabelFrame(main_frame, text='📁 导入话单', font=('Microsoft YaHei', 12), padx=15, pady=15)
        import_frame.pack(fill='x', pady=(0, 15))
        
        btn_frame = tk.Frame(import_frame)
        btn_frame.pack()
        tk.Button(btn_frame, text='📂 选择文件', font=('Microsoft YaHei', 11), command=self.select_files, bg='#4facfe', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🚀 开始分析', font=('Microsoft YaHei', 11), command=self.start_analysis, bg='#38ef7d', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🗑️ 清除', font=('Microsoft YaHei', 11), command=self.clear_data, bg='#f5576c', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        
        self.file_label = tk.Label(import_frame, text='请选择话单文件（支持 CSV、XLS、XLSX）', font=('Microsoft YaHei', 10), fg='#888')
        self.file_label.pack(pady=10)
        
        self.status_label = tk.Label(import_frame, text='', font=('Microsoft YaHei', 11), fg='#ff6b6b')
        self.status_label.pack()
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        self.tab_stats = tk.Frame(self.notebook)
        self.tab_contacts = tk.Frame(self.notebook)
        self.tab_time = tk.Frame(self.notebook)
        self.tab_location = tk.Frame(self.notebook)
        self.tab_network = tk.Frame(self.notebook)
        self.tab_long = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_stats, text='📊 统计')
        self.notebook.add(self.tab_contacts, text='👥 联系人')
        self.notebook.add(self.tab_time, text='⏰ 时间')
        self.notebook.add(self.tab_location, text='🌍 地理')
        self.notebook.add(self.tab_network, text='🔗 关联')
        self.notebook.add(self.tab_long, text='📞 长时间')
        
        self.setup_stats_tab()
        self.setup_contacts_tab()
        self.setup_time_tab()
        self.setup_location_tab()
        self.setup_network_tab()
        self.setup_long_tab()
    
    def setup_stats_tab(self):
        cards_frame = tk.Frame(self.tab_stats)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        self.stat_cards = []
        colors = ['#667eea', '#11998e', '#f093fb', '#4facfe', '#ff6b6b', '#ffd93d']
        labels = ['总通话', '总时长', '平均', '联系人数', '长时间', '熬夜%']
        for i, (color, label) in enumerate(zip(colors, labels)):
            card = tk.Frame(cards_frame, bg=color, padx=15, pady=12)
            card.grid(row=0, column=i, padx=5, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text='-', font=('Microsoft YaHei', 18, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Microsoft YaHei', 9), fg='white', bg=color).pack()
            self.stat_cards.append(card)
        
        self.type_label = tk.Label(self.tab_stats, text='', font=('Microsoft YaHei', 10))
        self.type_label.pack(pady=10)
    
    def setup_contacts_tab(self):
        cols = ['号码', '次数', '时长', '最后', '归属地']
        frame = tk.Frame(self.tab_contacts)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(frame, columns=cols, show='headings', height=25)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.contact_table = tree
    
    def setup_time_tab(self):
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
        
        hour_frame = tk.LabelFrame(self.tab_time, text='📊 小时分布（22:00-06:00熬夜）', font=('Microsoft YaHei', 11), padx=10, pady=10)
        hour_frame.pack(fill='x', padx=10, pady=5)
        self.hour_canvas = tk.Canvas(hour_frame, height=150, bg='white')
        self.hour_canvas.pack(fill='x', pady=5)
        
        week_frame = tk.LabelFrame(self.tab_time, text='📅 星期分布', font=('Microsoft YaHei', 11), padx=10, pady=10)
        week_frame.pack(fill='x', padx=10, pady=5)
        self.week_frame = tk.Frame(week_frame)
        self.week_frame.pack(fill='x')
    
    def setup_location_tab(self):
        cols = ['地区', '次数', '时长', '独立号码']
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
        self.network_info = tk.Label(self.tab_network, text='号码关联网络', font=('Microsoft YaHei', 12))
        self.network_info.pack(anchor='w', padx=10, pady=10)
        
        cols = ['号码', '关联数', '关联号码']
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
    
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[('话单文件', '*.csv *.xls *.xlsx'), ('所有文件', '*.*')])
        if files:
            self.selected_files = files
            names = ', '.join([os.path.basename(f) for f in files[:3]])
            if len(files) > 3:
                names += '...'
            self.file_label.config(text=f'已选择 {len(files)} 个文件: {names}')
            self.status_label.config(text='')
    
    def start_analysis(self):
        if not hasattr(self, 'selected_files') or not self.selected_files:
            self.status_label.config(text='⚠️ 请先选择话单文件！', fg='#ff6b6b')
            return
        
        self.analyzer.calls = []
        self.filtered_calls = None
        self.status_label.config(text='⏳ 正在分析...', fg='#667eea')
        self.root.update()
        
        try:
            for file_path in self.selected_files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.csv':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        calls = self.analyzer.parse_csv(f.read())
                    self.analyzer.calls.extend(calls)
                elif ext == '.xls':
                    calls = self.analyzer.parse_xls(file_path)
                    self.analyzer.calls.extend(calls)
                elif ext == '.xlsx':
                    calls = self.analyzer.parse_xlsx(file_path)
                    self.analyzer.calls.extend(calls)
            
            if self.analyzer.last_error:
                self.status_label.config(text=f'⚠️ {self.analyzer.last_error}', fg='#ff6b6b')
                messagebox.showerror('错误', self.analyzer.last_error)
                return
            
            if len(self.analyzer.calls) == 0:
                self.status_label.config(text='⚠️ 未解析到任何通话记录！', fg='#ff6b6b')
                messagebox.showerror('错误', '未解析到任何通话记录，请检查文件格式')
                return
            
            self.update_all_tabs()
            self.status_label.config(text=f'✅ 分析完成！共 {len(self.analyzer.calls)} 条通话记录', fg='#38ef7d')
            messagebox.showinfo('完成', f'分析完成！共 {len(self.analyzer.calls)} 条通话记录')
            
        except Exception as e:
            self.status_label.config(text=f'⚠️ 出错: {str(e)}', fg='#ff6b6b')
            messagebox.showerror('错误', str(e))
    
    def clear_data(self):
        self.analyzer.calls = []
        self.filtered_calls = None
        self.selected_files = []
        self.file_label.config(text='请选择话单文件（支持 CSV、XLS、XLSX）')
        self.status_label.config(text='')
        self.update_all_tabs()
    
    def update_all_tabs(self):
        self.update_stats()
        self.update_contacts()
        self.update_time()
        self.update_location()
        self.update_network()
        self.update_long()
    
    def update_stats(self):
        stats = self.analyzer.get_statistics(self.filtered_calls)
        values = [f"{stats['total_calls']} 次", stats['total_duration'], stats['avg_duration'], 
                  f"{len(self.analyzer.get_contact_analysis()['top']} 人", f"{stats['long_calls_count']} 次", f"{stats['night_rate']}%"]
        
        for i, (card, value) in enumerate(zip(self.stat_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=value, font=('Microsoft YaHei', 18, 'bold') if i < 4 else ('Microsoft YaHei', 12))
        
        incoming, outgoing = stats['incoming'], stats['outgoing']
        total = incoming + outgoing
        self.type_label.config(text=f'主叫: {outgoing} 次 ({round(outgoing/total*100) if total > 0 else 0}%)  |  被叫: {incoming} 次 ({round(incoming/total*100) if total > 0 else 0}%)')
    
    def update_contacts(self):
        contacts = self.analyzer.get_contact_analysis()
        for item in self.contact_table.get_children():
            self.contact_table.delete(item)
        for c in contacts['top'][:50]:
            self.contact_table.insert('', 'end', values=[c['phone'], c['count'], c['duration'], c['last_call'], c['locations'][:20]])
    
    def update_time(self):
        time_data = self.analyzer.get_time_analysis(self.filtered_calls)
        values = [', '.join(time_data['peak_hours']), time_data['peak_day'], f"{time_data['night_rate']}%", 
                  f"{time_data['morning_calls']} 次", f"{time_data['afternoon_calls']} 次"]
        
        for i, (card, value) in enumerate(zip(self.time_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=value, font=('Microsoft YaHei', 12, 'bold'))
        
        self.root.update()
        
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
        
        for widget in self.week_frame.winfo_children():
            widget.destroy()
        
        day_data = time_data['day_dist']
        days = time_data['day_names']
        max_day = max(day_data) if max(day_data) > 0 else 1
        
        for i, (day, count) in enumerate(zip(days, day_data)):
            frame = tk.Frame(self.week_frame)
            frame.pack(side='left', expand=True, padx=2)
            h = (count / max_day) * 80
            bar = tk.Frame(frame, width=35, height=80, bg='#eee')
            bar.pack()
            bar.pack_propagate(False)
            fill = tk.Frame(bar, width=35, height=int(h), bg='#667eea')
            fill.place(relx=0.5, y=80-int(h), anchor='n')
            tk.Label(frame, text=day, font=('Microsoft YaHei', 9)).pack()
            tk.Label(frame, text=str(count), font=('Microsoft YaHei', 8), fg='#888').pack()
    
    def update_location(self):
        locations = self.analyzer.get_location_analysis()
        for item in self.location_table.get_children():
            self.location_table.delete(item)
        for loc in locations:
            self.location_table.insert('', 'end', values=[loc['location'], f"{loc['count']} 次", loc['duration'], f"{loc['unique_phones']} 个"])
    
    def update_network(self):
        network = self.analyzer.get_number_network()
        self.network_info.config(text=f"网络规模: {network['network_size']} 个主号码  |  关联hub数: {len(network['hubs'])}")
        for item in self.network_table.get_children():
            self.network_table.delete(item)
        for hub in network['hubs']:
            self.network_table.insert('', 'end', values=[hub['phone'], f"{hub['connections']} 个", ', '.join(hub['numbers'][:5])])
    
    def update_long(self):
        stats = self.analyzer.get_statistics(self.filtered_calls)
        for item in self.long_table.get_children():
            self.long_table.delete(item)
        for c in stats['long_calls']:
            self.long_table.insert('', 'end', values=[c['start_time'], c['phone'], c['type'], f"{c['duration']}秒", c.get('phone_location', '-')])

if __name__ == '__main__':
    root = tk.Tk()
    app = CallAnalyzerApp(root)
    root.mainloop()
