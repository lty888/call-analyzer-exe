# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import os
from datetime import datetime
import re

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
        for idx, h in enumerate(headers[:8]):
            h_clean = h.replace(' ', '').replace('　', '')
            if '开始时间' in h_clean:
                col_indices['start_time'] = idx
            elif '事件类型' in h_clean or '类型' in h_clean:
                col_indices['type'] = idx
            elif '用户号码' in h_clean:
                col_indices['user_phone'] = idx
            elif '通话时长' in h_clean:
                col_indices['duration'] = idx
            elif '对端号码' in h_clean or '对方号码' in h_clean:
                col_indices['phone'] = idx
        
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
                
                phone = str(parts[phone_idx]).strip().strip('"') if phone_idx < len(parts) else ''
                duration = str(parts[duration_idx]).strip().strip('"') if duration_idx < len(parts) else '0'
                call_type = str(parts[type_idx]).strip().strip('"') if type_idx >= 0 and type_idx < len(parts) else ''
                start_time = str(parts[time_idx]).strip().strip('"') if time_idx >= 0 and time_idx < len(parts) else ''
                user_phone = str(parts[user_phone_idx]).strip().strip('"') if user_phone_idx >= 0 and user_phone_idx < len(parts) else ''
                
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
                    'duration_sec': self.parse_duration(duration)
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
            for i in range(min(5, sheet.nrows)):
                row_values = sheet.row_values(i)
                if '开始时间' in str(row_values):
                    header_row = i
                    break
            
            if header_row is None:
                print('未找到"开始时间"列')
                return calls
            
            headers = sheet.row_values(header_row)
            print(f'XLS列名: {headers[:8]}')
            
            col_indices = {}
            for idx, h in enumerate(headers[:8]):
                h_str = str(h).replace(' ', '').replace('　', '')
                if '开始时间' in h_str:
                    col_indices['start_time'] = idx
                elif '事件类型' in h_str or h_str == '类型':
                    col_indices['type'] = idx
                elif '用户号码' in h_str:
                    col_indices['user_phone'] = idx
                elif '通话时长' in h_str:
                    col_indices['duration'] = idx
                elif '对端号码' in h_str or '对方号码' in h_str:
                    col_indices['phone'] = idx
            
            print(f'XLS列索引: {col_indices}')
            
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
                    
                    phone = str(row[phone_idx].value).strip() if phone_idx < len(row) else ''
                    duration = str(row[duration_idx].value).strip() if duration_idx < len(row) else '0'
                    call_type = str(row[type_idx].value).strip() if type_idx >= 0 and type_idx < len(row) else ''
                    start_time = str(row[time_idx].value).strip() if time_idx >= 0 and time_idx < len(row) else ''
                    user_phone = str(row[user_phone_idx].value).strip() if user_phone_idx >= 0 and user_phone_idx < len(row) else ''
                    
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
                        'duration_sec': self.parse_duration(duration)
                    })
                    data_count += 1
                except:
                    continue
            
            print(f'XLS解析到 {data_count} 条记录')
            return calls
        except Exception as e:
            print(f'解析xls失败: {e}')
            return []
    
    def parse_xlsx(self, file_path):
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            calls = []
            
            print(f'XLSX列名: {df.columns.tolist()[:8]}')
            
            cols = df.columns.tolist()
            col_map = {}
            for c in cols:
                c_clean = c.replace(' ', '')
                if '开始时间' in c_clean:
                    col_map['start_time'] = c
                elif '对端号码' in c_clean:
                    col_map['phone'] = c
                elif '通话时长' in c_clean:
                    col_map['duration'] = c
                elif '事件类型' in c_clean:
                    col_map['type'] = c
                elif '用户号码' in c_clean:
                    col_map['user_phone'] = c
            
            for _, row in df.iterrows():
                try:
                    phone = str(row.get(col_map.get('phone', '对端号码'), '')).strip()
                    if not phone:
                        continue
                    
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    if len(phone_clean) < 7:
                        continue
                    
                    user_phone = str(row.get(col_map.get('user_phone', '用户号码'), '')).strip()
                    user_phone_clean = re.sub(r'[^\d]', '', user_phone)
                    if user_phone_clean and phone_clean == user_phone_clean:
                        continue
                    
                    duration = str(row.get(col_map.get('duration', '通话时长'), '0'))
                    calls.append({
                        'type': str(row.get(col_map.get('type', '事件类型'), '')).strip(),
                        'phone': phone,
                        'start_time': str(row.get(col_map.get('start_time', '开始时间'), '')).strip(),
                        'duration': duration,
                        'duration_sec': self.parse_duration(duration),
                    })
                except:
                    continue
            
            print(f'XLSX解析到 {len(calls)} 条记录')
            return calls
        except Exception as e:
            print(f'解析xlsx失败: {e}')
            return []
    
    def set_user_phone(self, phone):
        self.user_phone = phone
        self.calls = [c for c in self.calls if c['phone'] != phone]
    
    def get_statistics(self):
        total_calls = len(self.calls)
        total_duration = sum(c['duration_sec'] for c in self.calls)
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        seconds = total_duration % 60
        incoming = len([c for c in self.calls if '被叫' in c['type']])
        outgoing = len([c for c in self.calls if '主叫' in c['type']])
        return {
            'total_calls': total_calls,
            'total_duration': f'{hours}小时{minutes}分{seconds}秒',
            'avg_duration': f'{total_duration // total_calls if total_calls > 0 else 0}秒',
            'incoming': incoming,
            'outgoing': outgoing
        }
    
    def get_contacts(self):
        contact_map = {}
        for c in self.calls:
            phone = c['phone']
            if phone not in contact_map:
                contact_map[phone] = {'phone': phone, 'count': 0, 'total_duration': 0, 'last_call': c['start_time']}
            contact_map[phone]['count'] += 1
            contact_map[phone]['total_duration'] += c['duration_sec']
            if c['start_time'] > contact_map[phone]['last_call']:
                contact_map[phone]['last_call'] = c['start_time']
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
                'last_call': data['last_call'].split(' ')[0] if data['last_call'] else '-'
            })
        contacts.sort(key=lambda x: x['count'], reverse=True)
        strangers = [c for c in contacts if c['count'] == 1]
        frequent = [c for c in contacts if c['count'] > 20]
        return {'top': contacts[:50], 'strangers': strangers[:50], 'frequent': frequent[:50]}
    
    def get_time_analysis(self):
        hour_dist = [0] * 24
        day_dist = [0] * 7
        days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        
        for c in self.calls:
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
        
        print(f'时间分析: 高峰时段={peak_hours}, 高峰日={peak_day}, 熬夜={night_calls}次')
        
        return {
            'hour_dist': hour_dist,
            'day_dist': day_dist,
            'day_names': days,
            'peak_hours': peak_hours,
            'peak_day': peak_day,
            'night_calls': night_calls,
            'night_rate': round(night_calls / len(self.calls) * 100) if self.calls else 0
        }

class CallAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('话单分析工具 v1.0')
        self.root.geometry('1000x700')
        self.analyzer = CallAnalyzer()
        self.setup_ui()
        
        # 强制更新窗口大小
        self.root.update_idletasks()
    
    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg='#667eea', pady=15)
        top_frame.pack(fill='x')
        tk.Label(top_frame, text='📱 话单分析工具', font=('Microsoft YaHei', 18, 'bold'), fg='white', bg='#667eea').pack()
        tk.Label(top_frame, text='支持 CSV、XLS、XLSX 格式', font=('Microsoft YaHei', 10), fg='white', bg='#667eea').pack()
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        import_frame = tk.LabelFrame(main_frame, text='📁 导入话单', font=('Microsoft YaHei', 12), padx=15, pady=15)
        import_frame.pack(fill='x', pady=(0, 20))
        
        btn_frame = tk.Frame(import_frame)
        btn_frame.pack()
        tk.Button(btn_frame, text='📂 选择话单文件', font=('Microsoft YaHei', 11), command=self.select_files, bg='#4facfe', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🚀 开始分析', font=('Microsoft YaHei', 11), command=self.start_analysis, bg='#38ef7d', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        tk.Button(btn_frame, text='🗑️ 清除', font=('Microsoft YaHei', 11), command=self.clear_data, bg='#f5576c', fg='white', padx=15, pady=8).pack(side='left', padx=5)
        
        self.file_label = tk.Label(import_frame, text='支持 CSV、XLS、XLSX 格式，可多选', font=('Microsoft YaHei', 10), fg='#888')
        self.file_label.pack(pady=10)
        
        phone_frame = tk.Frame(import_frame)
        phone_frame.pack(pady=10)
        tk.Label(phone_frame, text='📱 我的手机号（过滤自己的号码）:', font=('Microsoft YaHei', 10)).pack(side='left')
        self.phone_entry = tk.Entry(phone_frame, font=('Microsoft YaHei', 10), width=15)
        self.phone_entry.pack(side='left', padx=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        self.tab_stats = tk.Frame(self.notebook)
        self.tab_contacts = tk.Frame(self.notebook)
        self.tab_time = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_stats, text='📊 通话统计')
        self.notebook.add(self.tab_contacts, text='👥 联系人分析')
        self.notebook.add(self.tab_time, text='⏰ 时间分析')
        
        self.setup_stats_tab()
        self.setup_contacts_tab()
        self.setup_time_tab()
    
    def setup_stats_tab(self):
        cards_frame = tk.Frame(self.tab_stats)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        self.stat_cards = []
        colors = ['#667eea', '#11998e', '#f093fb', '#4facfe']
        labels = ['总通话次数', '总通话时长', '平均时长', '联系人数']
        for i, (color, label) in enumerate(zip(colors, labels)):
            card = tk.Frame(cards_frame, bg=color, padx=20, pady=15)
            card.grid(row=0, column=i, padx=5, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text='-', font=('Microsoft YaHei', 20, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Microsoft YaHei', 10), fg='white', bg=color).pack()
            self.stat_cards.append(card)
        
        dist_frame = tk.LabelFrame(self.tab_stats, text='📈 主叫/被叫分布', font=('Microsoft YaHei', 11), padx=15, pady=15)
        dist_frame.pack(fill='x', padx=10, pady=10)
        
        self.incoming_bar = tk.Frame(dist_frame, bg='#38ef7d', height=20)
        self.incoming_bar.pack(fill='x', pady=2)
        tk.Label(dist_frame, text='被叫: 0 次', font=('Microsoft YaHei', 10), anchor='w').pack(fill='x')
        
        self.outgoing_bar = tk.Frame(dist_frame, bg='#4facfe', height=20)
        self.outgoing_bar.pack(fill='x', pady=2)
        tk.Label(dist_frame, text='主叫: 0 次', font=('Microsoft YaHei', 10), anchor='w').pack(fill='x')
    
    def setup_contacts_tab(self):
        sub_notebook = ttk.Notebook(self.tab_contacts)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.tab_freq = tk.Frame(sub_notebook)
        self.tab_stranger = tk.Frame(sub_notebook)
        self.tab_frequent = tk.Frame(sub_notebook)
        
        sub_notebook.add(self.tab_freq, text='🔥 通话频次')
        sub_notebook.add(self.tab_stranger, text='👤 陌生人')
        sub_notebook.add(self.tab_frequent, text='⭐ 高频联系人')
        
        self.create_table(self.tab_freq, ['排名', '号码', '次数', '时长', '最后通话'], 'freq_table')
        self.create_table(self.tab_stranger, ['号码', '时长', '日期'], 'stranger_table')
        self.create_table(self.tab_frequent, ['号码', '次数', '时长'], 'frequent_table')
    
    def setup_time_tab(self):
        # 高峰时段卡片
        cards_frame = tk.Frame(self.tab_time)
        cards_frame.pack(fill='x', padx=10, pady=10)
        
        self.time_cards = []
        colors = ['#667eea', '#11998e', '#f093fb', '#4facfe']
        labels = ['高峰时段', '高峰日', '熬夜次数', '熬夜占比']
        for i, (color, label) in enumerate(zip(colors, labels)):
            card = tk.Frame(cards_frame, bg=color, padx=15, pady=12)
            card.grid(row=0, column=i, padx=5, sticky='ew')
            cards_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text='-', font=('Microsoft YaHei', 16, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Microsoft YaHei', 9), fg='white', bg=color).pack()
            self.time_cards.append(card)
        
        # 小时分布图
        hour_frame = tk.LabelFrame(self.tab_time, text='📊 按小时分布（22:00-06:00为熬夜时段）', font=('Microsoft YaHei', 11), padx=15, pady=15)
        hour_frame.pack(fill='x', padx=10, pady=10)
        self.hour_canvas = tk.Canvas(hour_frame, height=120, bg='white')
        self.hour_canvas.pack(fill='x', pady=5)
        
        # 星期分布图
        week_frame = tk.LabelFrame(self.tab_time, text='📅 按星期分布', font=('Microsoft YaHei', 11), padx=15, pady=15)
        week_frame.pack(fill='x', padx=10, pady=10)
        self.week_frame = tk.Frame(week_frame)
        self.week_frame.pack(fill='x')
    
    def create_table(self, parent, columns, var_name):
        frame = tk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        setattr(self, var_name, tree)
    
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[('话单文件', '*.csv *.xls *.xlsx'), ('CSV文件', '*.csv'), ('Excel文件', '*.xls *.xlsx'), ('所有文件', '*.*')])
        if files:
            self.selected_files = files
            self.file_label.config(text=f'已选择 {len(files)} 个文件')
    
    def start_analysis(self):
        if not hasattr(self, 'selected_files') or not self.selected_files:
            messagebox.showwarning('警告', '请先选择话单文件')
            return
        
        self.analyzer.calls = []
        phone = self.phone_entry.get().strip()
        if phone:
            self.analyzer.set_user_phone(phone)
        
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
        
        self.update_stats()
        self.update_contacts()
        self.update_time()
        messagebox.showinfo('完成', f'分析完成！共 {len(self.analyzer.calls)} 条通话记录')
    
    def update_stats(self):
        stats = self.analyzer.get_statistics()
        contacts = self.analyzer.get_contacts()
        values = [f"{stats['total_calls']} 次", stats['total_duration'], stats['avg_duration'], f"{len(contacts['top'])} 人"]
        
        for i, (card, value) in enumerate(zip(self.stat_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    try:
                        int(value.split()[0])
                        child.config(text=value, font=('Microsoft YaHei', 20, 'bold'))
                    except:
                        child.config(text=value, font=('Microsoft YaHei', 14))
        
        incoming = stats['incoming']
        outgoing = stats['outgoing']
        total = incoming + outgoing
        
        for widget in self.incoming_bar.master.winfo_children():
            if isinstance(widget, tk.Label) and '被叫' in widget.cget('text'):
                widget.config(text=f'被叫: {incoming} 次 ({round(incoming/total*100) if total > 0 else 0}%)')
        for widget in self.outgoing_bar.master.winfo_children():
            if isinstance(widget, tk.Label) and '主叫' in widget.cget('text'):
                widget.config(text=f'主叫: {outgoing} 次 ({round(outgoing/total*100) if total > 0 else 0}%)')
        
        self.incoming_bar.config(width=max(1, int(300 * incoming / total)) if total > 0 else 1)
        self.outgoing_bar.config(width=max(1, int(300 * outgoing / total)) if total > 0 else 1)
    
    def update_contacts(self):
        contacts = self.analyzer.get_contacts()
        
        for item in self.freq_table.get_children():
            self.freq_table.delete(item)
        for i, c in enumerate(contacts['top'][:20], 1):
            self.freq_table.insert('', 'end', values=[i, c['phone'], f"{c['count']} 次", c['duration'], c['last_call']])
        
        for item in self.stranger_table.get_children():
            self.stranger_table.delete(item)
        for c in contacts['strangers']:
            self.stranger_table.insert('', 'end', values=[c['phone'], c['duration'], c['last_call']])
        
        for item in self.frequent_table.get_children():
            self.frequent_table.delete(item)
        for c in contacts['frequent']:
            self.frequent_table.insert('', 'end', values=[c['phone'], f"{c['count']} 次", c['duration']])
    
    def update_time(self):
        time_data = self.analyzer.get_time_analysis()
        
        values = [', '.join(time_data['peak_hours']), time_data['peak_day'], f"{time_data['night_calls']} 次", f"{time_data['night_rate']}%"]
        
        for i, (card, value) in enumerate(zip(self.time_cards, values)):
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text=value, font=('Microsoft YaHei', 14, 'bold'))
        
        # 强制更新窗口
        self.root.update()
        
        # 绘制小时柱状图
        self.hour_canvas.delete('all')
        hour_data = time_data['hour_dist']
        max_hour = max(hour_data) if max(hour_data) > 0 else 1
        
        # 获取画布实际宽度
        canvas_width = self.hour_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 800  # 默认宽度
        
        bar_width = max(15, (canvas_width - 80) / 24)
        
        for i, count in enumerate(hour_data):
            height = (count / max_hour) * 100
            x = 40 + i * bar_width
            y = 120 - height
            # 蓝色=白天(8-22点)，红色=熬夜(22-6点)
            color = '#667eea' if 8 <= i <= 22 else '#f5576c'
            self.hour_canvas.create_rectangle(x, y, x + bar_width - 2, 120, fill=color, outline='')
            if count > 0:
                self.hour_canvas.create_text(x + bar_width/2, y - 5, text=str(count), font=('Arial', 8))
        
        # 绘制星期柱状图
        for widget in self.week_frame.winfo_children():
            widget.destroy()
        
        day_data = time_data['day_dist']
        days = time_data['day_names']
        max_day = max(day_data) if max(day_data) > 0 else 1
        
        for i, (day, count) in enumerate(zip(days, day_data)):
            frame = tk.Frame(self.week_frame)
            frame.pack(side='left', expand=True, padx=3)
            height = (count / max_day) * 80
            bar = tk.Frame(frame, width=30, height=80, bg='#eee')
            bar.pack()
            bar.pack_propagate(False)
            fill = tk.Frame(bar, width=30, height=int(height), bg='#667eea')
            fill.place(relx=0.5, y=80-int(height), anchor='n')
            tk.Label(frame, text=day, font=('Microsoft YaHei', 9)).pack()
            tk.Label(frame, text=str(count), font=('Microsoft YaHei', 8), fg='#888').pack()
    
    def clear_data(self):
        self.analyzer.calls = []
        self.analyzer.user_phone = ''
        self.selected_files = []
        self.file_label.config(text='支持 CSV、XLS、XLSX 格式，可多选')
        self.phone_entry.delete(0, 'end')
        
        for item in self.freq_table.get_children():
            self.freq_table.delete(item)
        for item in self.stranger_table.get_children():
            self.stranger_table.delete(item)
        for item in self.frequent_table.get_children():
            self.frequent_table.delete(item)
        
        for card in self.stat_cards:
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(text='-')
        
        self.incoming_bar.config(width=1)
        self.outgoing_bar.config(width=1)

if __name__ == '__main__':
    root = tk.Tk()
    app = CallAnalyzerApp(root)
    root.mainloop()
