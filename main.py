import os # 標準
import re # 標準
import customtkinter as ctk # pip install customtkinter
import pyperclip # pip install pyperclip
import webbrowser # 標準
import markdown # pip install markdown
from functools import partial # 標準
from collections import deque # 標準
from tkinter import Canvas, messagebox # 標準
from PIL import Image # pip install pillow
from tkhtmlview import HTMLLabel # pip install tkhtmlview

PATH="./data" # 検索ディレクトリ
FONT = "meiryo UI"# 左側のフォント(初期値:"meiryo UI")
FONTSIZE=16 # フォントサイズ
MDFONT="Noto Sans CJK JP" # MDファイルのフォント(初期値:"Noto Sans CJK JP")
MDFONTSIZE=16 # MDファイルのフォントサイズ(おススメ:16)
MDCODEFONT="Courier New" # MDファイルのコード用フォント(初期値:"Courier New")
EXCEPTION_FILE_NAME=["pic"] # 検索から除外するフォルダ名

class Md_viewer(ctk.CTkScrollableFrame):
	def __init__(self,master):
		super().__init__(master)
		self.Object=[]
		self.enum_num=[]#{"space":spaceの量,"num":番号}
		self.code_buffer=[]
		self.line_is_code=False
	def make_md_view(self, path):
		#新しい盤面の生成
		try:
			with open(path, 'r', encoding='utf-8') as f:
				text = f.read()#markdownファイルの読み込み
		except OSError as e:
			messagebox.showinfo('error', f"データの読み込みに失敗しました: {e}")
			text = None
		text = text.split('\n')# textを改行で分割
		# textを1行ずつ解析
		for line in text:
			if self.line_is_code==True:
				self.code_analysis(line)
			else:
				self.Object.append(self.line_analysis(line))
		# tkObjectの要素を1つずつframeに追加
		for i in self.Object:
			i.pack(anchor="nw")

	def line_analysis(self, line):
		line=re.sub("\t","    ",line)# tab -> space*4に変換
		# 構造化パターンマッチングを使って、textを解析
		match StrRe(line):
			# lineが#+半角スペースで始まる場合
			case "#+ ":
				self.enum_num.clear()#番号付き箇条書きの番号をリセット
				count = line.count("#")# lineが#で始まる場合、#の数を取得
				line = line.replace("#", "")# lineから#を削除
				line = line.strip()# lineの前後の空白を削除
				# labelを作成
				label = ctk.CTkLabel(self, text=line, font=(MDFONT, MDFONTSIZE + (6 - count) *3), 
						 justify="left",wraplength=self.framewidth, fg_color="transparent")
				return label
			
			# lineの文頭が{space}* + { * or - or + } + {space} -> 箇条書きリスト
			case "^\s*[\*\-\+]\s":
				line = re.sub("^[\*\-\+]", "・",line)#文頭の*,-,+を・に置換
				line = re.sub("(?<=\s)[\*\-\+]", "・",line)#空白の後の*,-,+を・に置換
				label = ctk.CTkLabel(self, text=line, font=(MDFONT, MDFONTSIZE), wraplength=self.framewidth, justify="left",fg_color="transparent")
				return label
			
			# lineの文頭が{space}* + {num} + "." + {space} -> 番号付きリスト
			case "^\s*\d+\.":
				# まずインデント量の検出(spaceの数で判定)
				indent=re.search("^\s*",line)
				indent_size=len(indent.group())
				num=-1

				# 番号が保存されている場合
				for i in self.enum_num:
					if i["space"]==indent_size:
						num=i["num"]
						i["num"]=num+1
					elif i["space"]>indent_size:
						i["num"]=1

				# 番号が保存されていない場合
				if num==-1:
					self.enum_num.append({"space":indent_size,"num":2})
					num=1

				line = re.sub("^\d+\.", f"{num}.", line)# 文頭の数字を行番号に置換
				line = re.sub("(?<=\s)\d+\.", f"{num}.",line)# 空白の後の数字を行番号に置換
				# self.enum_num+=1
				label = ctk.CTkLabel(self, text=line, font=(MDFONT, MDFONTSIZE), wraplength=self.framewidth, justify="left",fg_color="transparent")
				return label
			
			# lineの文頭が"---" or "***" or "___" -> 水平線を作成
			case "---"|"\*\*\*"|"___":
				self.enum_num.clear()#番号付き箇条書きの番号をリセット
				canvas = Canvas(self, width=self.framewidth, height=1, background="gray30", highlightthickness=0)
				return canvas
			
			# lineの文頭が"```" -> 以降の文をソースコードとして扱う。
			case "```":
				self.enum_num.clear()#番号付き箇条書きの番号をリセット
				self.line_is_code=True
				label = ctk.CTkLabel(self, text="",fg_color="transparent")#ダミー
				return label

			# lineの文頭が"![" -> pathを取得して画像を張る。
			case r"!\[":
				self.enum_num.clear()#番号付き箇条書きの番号をリセット
				
				line = re.findall(r'\((.*?)\)', line)[0].replace("^.\\", "")
				line = os.path.join(os.path.dirname(__file__), line)			
				try:
					image=Image.open(line)
					image_width = self.framewidth if image.width > self.framewidth else image.width
					image_height = (image.height * image_width) / image.width
					ctk_image = ctk.CTkImage(light_image=image,
									dark_image=image,
									size=(image_width, image_height))
					image_label = ctk.CTkLabel(self, image=ctk_image, text="")  # display image with a CTkLabel
					return image_label
				except OSError as e:
					messagebox.showinfo('error', f"画像の読み込みに失敗しました: {e}")
					label = ctk.CTkLabel(self, text="",fg_color="transparent")#ダミー
					return label
				
			# 文頭が"[title](url)" -> urlとして扱う。
			case r"\[.*\]\(.*\)":
				link_url = re.findall(r'\((.*?)\)', line)[0]
				link_title = re.findall(r'\[(.*?)\]', line)[0]
				link_label=ctk.CTkLabel(self, text=link_title, font=(MDFONT, MDFONTSIZE,"underline"), 
							wraplength=self.framewidth, justify="left", fg_color="transparent", text_color="#0000ff",)
				link_label.bind("<Button-1>",lambda e: webbrowser.open_new_tab(link_url))
				return link_label
			
			# そのほかの場合は単純なlabelを作成
			case _:
				label = ctk.CTkLabel(self, text=line, font=(MDFONT, MDFONTSIZE),
						 wraplength=self.framewidth, justify="left", fg_color="transparent")
				return label
			
	def code_analysis(self,line):
		#framewidth=self.master.winfo_width()
		# 構造化パターンマッチングを使って、textを解析
		match StrRe(line):
			case "```":
				self.line_is_code=False
				code= "\n".join(self.code_buffer)
				self.code_buffer.clear()
				textbox=ctk.CTkTextbox(self,font=(MDCODEFONT,MDFONTSIZE-4), width=self.framewidth, corner_radius=6, border_width=0, border_spacing=3, wrap="char")
				copy_button=ctk.CTkButton(self,font=('MS UI Gothic',MDFONTSIZE),text="copy", width=50, anchor="center", corner_radius=6, border_width=0, 
							  border_spacing=2, command=lambda:pyperclip.copy(code))
				textbox.insert("0.0",code)
				self.Object.append(textbox)
				self.Object.append(copy_button)
			case _:
				self.code_buffer.append(line)
		
	def set_frame_width(self,width):
		self.configure(width=width)
		self.framewidth=width

class StrRe(str):
	def __init__(self, var):
		self.var = var

	def __eq__(self, pattern):
		return True if re.search(pattern, self.var) is not None else False

class Md_viewer_html(ctk.CTkFrame):
	def __init__(self,master):
		super().__init__(master)

	def make_md_view(self, path):
		#新しい盤面の生成
		try:
			with open(path, 'r', encoding='utf-8') as f:
				text = f.read()#markdownファイルの読み込み
		except OSError as e:
			messagebox.showinfo('error', f"データの読み込みに失敗しました: {e}")
			text = None
		md=markdown.Markdown(extensions=['tables'])
		text=md.convert(text)
		html_label = HTMLLabel(self, html=text)
		html_label.pack(fill="both",side="bottom",expand=1)
		
	def set_frame_width(self,width):
		self.configure(width=width)
		self.framewidth=width

class File_viewer(ctk.CTkScrollableFrame):
	def __init__(self, master, path):
		super().__init__(master)
		self.left_frame=master
		self.path=path
		self.grid_columnconfigure(0, weight=1) #列の重み
		self.print_files(self.path)
		self.configure(fg_color="transparent")

	def print_files(self, path):
		if path==None:
			pass
		else:
			file_list = self.__get_files_and_folders(path)
			for i, file in enumerate(file_list):
				name=file["name"]
				if file["file"]==True:
					#ファイルボタンの追加
					button=ctk.CTkButton(self, text=name, anchor="w",font=(FONT,FONTSIZE,'bold'), 
						  corner_radius=0, border_width=0,command=partial(self.__select_file,file)
						  ,fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
					button.grid(row=i, column=0, sticky="ew")
				else:
					#フォルダボタンの追加
					button=ctk.CTkButton(self, text=f"{name} >",font=(FONT,FONTSIZE,'bold'),
						  anchor="w", corner_radius=0, border_width=0,command=partial(self.__select_dir,file)
						  ,fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
					button.grid(row=i, column=0, sticky="ew")

	def __get_files_and_folders(self,directory_path):
		#ディレクトリの読み込みとファイル名の取得(辞書順)。
		#返り値:{"name":name,"file":TrueorFalse,"path":path}
		try:
			all_items = sorted(os.listdir(directory_path))
			files = []
			for item in all_items:
				item_path = os.path.join(directory_path, item)
				if os.path.isfile(item_path) and re.match(r".*\.md$",item):
					files.append({"name":re.sub(r'\.md$', '', item),"file":True,"path":item_path})
				elif os.path.isdir(item_path) and not self.__check_regex_match(EXCEPTION_FILE_NAME,item):
					files.append({"name":item,"file":False,"path":item_path})
			return files
		except OSError as e:
			messagebox.showinfo('error', f"データの読み込みに失敗しました: {e}")
			return None
		
	def __check_regex_match(self, array, target_string):
		for pattern in array:
			if re.fullmatch(pattern, target_string):
				return True
		return False
		
	def __select_file(self,file):
		#ファイルが選択されたときの処理
		#引数:{"name":name,"file":TrueorFalse,"path":path}
		self.Right_frame.make_md_view(path=file["path"])
		self.file_name_label.configure(text=file["name"]+".md")#ファイル名の表示
		pass

	def __select_dir(self,file):
		#フォルダが選択されたときの処理
		#引数:{"name":name,"file":TrueorFalse,"path":path}|"prev"
		self.left_frame.Remake_File_viewer(file["path"])#親に自分自身の転生を申請

	def set_name_label(self,label):
		self.file_name_label=label

	def set_Right_frame(self,Right_frame):
		self.Right_frame=Right_frame

class Left_frame(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master)
		self.configure(corner_radius=0)
		self.path_deque=deque()
		self.path_deque.append(PATH)
		self.grid_rowconfigure(1, weight=1) #行の重み
		self.grid_columnconfigure(0, weight=1) #列の重み
		self.back_button=ctk.CTkButton(self, text="<<", anchor="center",
								command=self.back_button_callback,width=3,height=10)
		self.file_viewer_frame = File_viewer(self, path=PATH)#ファイル選択フレームのインスタンス化
		self.html_switch=ctk.CTkSwitch(self,text="HTML mode",
								  command=self.__shift_html_mode)#ナイトシフトスイッチ
		self.night_switch=ctk.CTkSwitch(self,text="night mode",
								  command=self.__shift_night_mode)#ナイトシフトスイッチ
		self.file_viewer_frame.grid(row=1, column=0, sticky="news")
		self.html_switch.grid(row=2, column=0, pady=(5, 10),padx=(15, 0), sticky="ws")
		self.night_switch.grid(row=3, column=0, pady=(5, 10),padx=(15, 0), sticky="ws")

	def __shift_night_mode(self):
		if self.night_switch.get()==1:
			mode="dark"
		else:
			mode="light"
		ctk.set_appearance_mode(mode)

	def __shift_html_mode(self):
		if self.html_switch.get()==1:
			self.Right_frame.set_html_mode(True)
		else:
			self.Right_frame.set_html_mode(False)
	
	def set_Right_frame(self,frame):
		self.Right_frame=frame
		self.file_viewer_frame.set_Right_frame(frame)

	def set_name_label(self,label):
		self.name_label=label
		self.file_viewer_frame.set_name_label(label)

	def set_visible_Backbutton(self):
		#戻るボタンの設定
		if len(self.path_deque)<=1:
			self.back_button.grid_forget()
		else:
			self.back_button.grid(row=0, column=0,sticky="w",ipady=3,padx=7, pady=(10,0))
	
	def Remake_File_viewer(self,path):
		self.path_deque.append(path)
		self.file_viewer_frame.destroy()
		self.file_viewer_frame = File_viewer(self, path=path)
		self.file_viewer_frame.set_name_label(self.name_label)#setter
		self.file_viewer_frame.set_Right_frame(self.Right_frame)#setter
		self.file_viewer_frame.grid(row=1, column=0, sticky="news")
		self.set_visible_Backbutton()

	def back_button_callback(self):
		if len(self.path_deque)<=1:
			pass
		else:
			self.path_deque.pop()
			path=self.path_deque.pop()
			self.Remake_File_viewer(path)

class Right_frame(ctk.CTkFrame):
	def __init__(self, master):
		super().__init__(master)
		self.configure(fg_color="transparent")
		self.grid_rowconfigure(1, weight=1) #行の重み
		self.grid_columnconfigure(0, weight=1) #列の重み
		self.html_mode=False
		self.md_viewer_frame = ctk.CTkFrame(self)#md表示用フレームのインスタンス化
		self.file_name_label = ctk.CTkLabel(self, text="", font=('MS UI Gothic', 20,"bold"),
									  anchor="w",fg_color="transparent")#ファイル名表示用ラベル
		self.file_name_label.grid(row=0, column=0, sticky="e")
		self.md_viewer_frame.grid(row=1, column=0, sticky="news")

	def make_md_view(self,path):
		prev_frame_width=self.md_viewer_frame.winfo_width()
		self.md_viewer_frame.destroy()#既存のframeは一度破棄
		if self.html_mode==True:
			self.md_viewer_frame = Md_viewer_html(self)#md表示用フレームのインスタンス化
		else:
			self.md_viewer_frame = Md_viewer(self)#md表示用フレームのインスタンス化
		#ctkでは描写処理中に自身のウィンドウフレームの大きさを取得すると初めのミリ秒のうちだけ大きさにかかわらず1が返ってきてしまうため
		#事前に直前まで使用したフレームの大きさを与えておく。
		self.md_viewer_frame.set_frame_width(width=prev_frame_width)
		self.md_viewer_frame.grid(row=1, column=0, sticky="news")
		self.md_viewer_frame.make_md_view(path=path)
	
	def get_name_label(self):
		return self.file_name_label
	
	def set_html_mode(self,bool):
		if bool==True:
			self.html_mode=bool
		elif bool==False:
			self.html_mode=bool

class App(ctk.CTk):
	def __init__(self):
		super().__init__()
		self.fonts = (FONT, 15)
		self.minsize(width=350,height=200)#画面の最小サイズの設定
		self.geometry("800x600")
		self.title("KyoproGUI")#ウィンドウタイトル
		self.grid_columnconfigure(1, weight=1) #列の重み
		self.grid_rowconfigure(0, weight=1) #行の重み
		ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
		ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
		self.make_frames()#ページ生成

	def make_frames(self):
		#右画面は左画面依存なので右画面を生成後にsetterメソッドで右画面の情報を左画面を担当するオブジェクトFile_viewerに渡す。
		self.Rightside_frame = Right_frame(self)#右画面のインスタンス化
		self.Leftside_frame = Left_frame(self)#左画面のインスタンス化
		self.Leftside_frame.set_Right_frame(self.Rightside_frame)#setter
		self.Leftside_frame.set_name_label(self.Rightside_frame.get_name_label())#setter
		self.Rightside_frame.grid(row=0, column=1, padx=(0,10), pady=(1, 0), sticky="news")
		self.Leftside_frame.grid(row=0, column=0, padx=(0,10), sticky="nws")

if __name__ == "__main__":
	# アプリケーション実行
	app = App()
	app.mainloop()

