
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox, filedialog #Tkinter Python Module for GUI  
import socket #Sockets for network connection
import threading # for multiple proccess 
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM

tokenizer=AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh")

model=AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-zh")

class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.translate=False
        self.b=False
        self.loadfile_button = None
        self.loadfile_text = None
        self.filename = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
        remote_ip = '127.0.0.1' # IP address 
        remote_port = 10319 #TCP port
        self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server

    def initialize_gui(self): # GUI initializer
        self.root.title("共同討論室") 
        self.root.resizable(0, 0)
        self.display_name_section()
        self.display_chat_box()
        self.display_chat_entry_box()
        self.display_document()
    
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()
    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
         
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " 已加入討論"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            elif ".txt" in message:
                self.filename = message.split(".txt")[0]+".txt"
                filedata = message.split(".txt")[1]
                self.loadfile_text.delete(1.0, 'end')
                self.loadfile_text.insert('end', filedata)
                self.loadfile_text.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()

    def display_name_section(self):
        frame = Frame()
        Label(frame, text='請輸入名字:', font=("Helvetica", 16)).pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="參與討論", width=10, command=self.on_join).pack(side='left')
        frame.pack(side='top', anchor='nw')

    def display_chat_box(self):
        frame = Frame()
        Label(frame, text='討論串:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, font=("Serif", 12))
        self.chat_transcript_area.pack(side='left',fill='y')
        clean_button = Button(frame, text="清除討論", width=15,height=15,command=self.clean_text)
        clean_button.pack(side='right')
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side='right',fill='y')
        scrollbar.config(command=self.chat_transcript_area.yview)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        
        #scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='輸入訊息:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=5, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        self.t_button = Button(frame, text="英翻中(關閉)", width=10,height=5,command=self.trans_button)
        self.t_button.pack(side='right')
        frame.pack(side='top')
    def display_document(self):
        frame = Frame()
        Label(frame, text='載入共同編輯文件:', font=(
            "Serif", 16)).pack(side='left', padx=10, anchor='nw')
        self.loadfile_button = Button(
            frame, text="選擇檔案", width=10, command=self.on_loadfile).pack(anchor='w')
        self.loadfile_text = Text(
            frame, width=69, height=20, font=("Serif", 12), highlightthickness=2, highlightbackground="black")
        self.loadfile_text.pack(side='left', padx=5, pady=5)
        self.join_button = Button(
            frame, text="送出", width=10, command=self.on_editfile).pack(side='bottom')
        frame.pack(side='top', anchor='nw')
        
    def on_editfile(self):
        data = self.loadfile_text.get('1.0', 'end')
        data_send = self.filename+data
        print(data_send)
        self.loadfile_text.delete(1.0, 'end')
        self.client_socket.sendall(data_send.encode('utf-8'))
        self.loadfile_text.insert('end', data)
        self.loadfile_text.yview(END)
        
    def on_loadfile(self):
        self.filename = filedialog.askopenfilename()
        f = open(self.filename, 'r')
        data = f.read()
        print(self.filename)
        data_send = self.filename+data
        self.client_socket.sendall(data_send.encode('utf-8'))
        self.loadfile_text.insert('end', data)
        self.loadfile_text.yview(END)
        
        
    def on_join(self):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return
        self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        if len(self.name_widget.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        data=self.trans(data)
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'
    
    def end_send_chat(self):
        senders_name = self.name_widget.get().strip() + " "
        data = "已離開討論"
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'
    
    def on_close_window(self):
        if messagebox.askokcancel("退出", "是否退出討論室?"):
            self.end_send_chat()
            self.root.destroy()
            #self.end_send_chat()
            self.client_socket.close()
            exit(0)
    
    def clean_text(self):
        self.chat_transcript_area.delete(1.0, 'end')
    
    def trans(self,data):
        if self.translate:
            batch=tokenizer.prepare_seq2seq_batch(src_texts=[data],return_tensors='pt')
            batch["input_ids"]=batch["input_ids"][:,:512]
            batch["attention_mask"]=batch["attention_mask"][:,:512]
            translation=model.generate(**batch)
            result=tokenizer.batch_decode(translation,skip_special_tokens=True)
            return result[0]
        else:
            return data
    def trans_button(self):
        if self.b:
            self.translate=False
            self.b=False
            self.t_button['text']='英翻中(關閉)'
        else:
            self.translate=True
            self.b=True
            self.t_button['text']='英翻中(開啟)'

#the mail function 
if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
