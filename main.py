from collections import deque
import customtkinter as ctk
from File_viewer import File_viewer
from Md_viewer import Md_viewer
from Md_viwer_html import Md_viewer_html

PATH="./data"#検索ディレクトリ
FONT = "meiryo UI"

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
		self.title("python_md_viewer")#ウィンドウタイトル
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
	
