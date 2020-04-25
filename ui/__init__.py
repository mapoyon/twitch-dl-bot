from tkinter import *
from tkinter.ttk import *
from queue import Queue, Empty
from buffer import RingBuffer
from twitch.bot import IRCBotManager


class LogBuffer(RingBuffer):
    BUF_LEN = 2000

    def __init__(self):
        super().__init__(self.BUF_LEN)

    def __delitem__(self, key):
        raise NotImplementedError


class LogList(Listbox):
    def __init__(self, master):
        frame = Frame(master)
        frame.pack(expand=True, fill=BOTH)
        source = LogBuffer()
        source_var = StringVar(value=tuple(source))
        scrollbar = Scrollbar(master=frame, orient=VERTICAL, command=self.yview)
        scrollbar.pack(side=RIGHT, fill=Y, expand=0)
        super().__init__(master=frame, listvariable=source_var, yscrollcommand=scrollbar.set)
        self.pack(side=LEFT, fill=BOTH, expand=1)
        self.frame = frame
        self.source = source
        self.source_var = source_var
        self.scrollbar = scrollbar

    def append(self, value):
        auto_scroll = False
        if self.nearest(self.winfo_height()) >= len(self.source) - 1:
            auto_scroll = True
        self.source.append(value)
        self.source_var.set(value=tuple(self.source))
        if auto_scroll:
            self.see(END)


class Application(Frame):
    UPDATE_LOG_INTERVAL = 200

    def __init__(self, root):
        super().__init__(master=root)
        root.title("Twitch DeepL Bot")
        root.geometry("480x600")
        root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.master = root
        self.log_list = LogList(self)
        self.queue = Queue()
        self.pack(expand=True, fill=BOTH)
        self.bot_manager = IRCBotManager()

    def shutdown(self):
        self.bot_manager.stop()
        self.master.destroy()

    def start_irc_bot(self):
        self.bot_manager.start(self.queue)

    def update_log(self):
        while True:
            try:
                item = self.queue.get(block=False)
            except Empty:
                break
            if item is None:
                break
            self.log_list.append(item)

    def schedule_update_log(self):
        self.after_idle(self.update_log)
        self.after(self.UPDATE_LOG_INTERVAL, self.schedule_update_log)

    def start(self):
        self.start_irc_bot()
        self.after(self.UPDATE_LOG_INTERVAL, self.schedule_update_log)
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
