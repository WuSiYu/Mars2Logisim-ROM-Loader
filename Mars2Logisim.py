import os
import itertools

import xml.etree.ElementTree

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


# 主窗口
window = tk.Tk()
window.configure(borderwidth='10')
window.resizable(0, 0)
window.title("MARS to Logisim ROM 加载器")


# 文件打开
MARS_HEX = tk.StringVar(window)
LOGISIM_XML = tk.StringVar(window)

def openMARS():
    global MARS_HEX
    MARS_HEX.set(filedialog.askopenfilename())

def openLogisim():
    global LOGISIM_XML
    LOGISIM_XML.set(filedialog.askopenfilename())


files_frame = tk.Frame(window)

tk.Label(files_frame, text="MARS Hex Dump 文件: ").grid(sticky="W", column=0, row=0)
ttk.Entry(files_frame, textvariable=MARS_HEX, state="disabled").grid(sticky="E", column=2, row=0)
ttk.Button(files_frame, text="打开...", command=openMARS).grid(sticky="E", column=3, row=0)

tk.Label(files_frame, text="Logisim .circ 文件: ").grid(sticky="W", column=0, row=1)
ttk.Entry(files_frame, textvariable=LOGISIM_XML, state="disabled").grid(sticky="E", column=2, row=1)
ttk.Button(files_frame, text="打开...", command=openLogisim).grid(sticky="E", column=3, row=1)

files_frame.pack(fill='x')


# 分割选项
tk.Label(window).pack()
ROM_width = tk.IntVar(window)
ROM_num = tk.IntVar(window)

config_frame = tk.Frame(window)

tk.Label(config_frame, text="单个ROM数据位宽: ").grid(sticky="W", column=0, row=0)
tk.Spinbox(config_frame, values=(4, 8, 16, 32), width=5, textvariable=ROM_width).grid(sticky="E", column=1, row=0)
ROM_width.set(8)

tk.Label(config_frame, text="ROM组件数量: ").grid(sticky="W", column=0, row=1)
tk.Spinbox(config_frame, from_=1, to=32, width=5, textvariable=ROM_num).grid(sticky="E", column=1, row=1)
ROM_num.set(4)

config_frame.pack(fill='x')

tk.Label(window, text="").pack()


# 执行
def run():
    f_mars = None
    rom_width = ROM_width.get()
    rom_num = ROM_num.get()
    try:

        # Mars Hex Dump 文件分割处理
        f_mars = open(MARS_HEX.get(), 'r')

        ROMs_contents = [[] for _ in range(rom_num)]

        def lines_to_stream(file):
            for line in file:
                line_it = iter(line[:-1])
                for seg in iter(lambda: ''.join(itertools.islice(line_it, rom_width // 4)), ''):
                    yield seg
        
        for rom, seg in zip(itertools.cycle(ROMs_contents), lines_to_stream(f_mars)):
            if not all(i in '0123456789abcdef' for i in seg):
                messagebox.showinfo("¿", "这MARS Hex Dump文件不太对劲")
                return
            rom.append(seg)
        
        # print(ROMs_contents)


        # Logisim .circ文件修改
        logisim_xml = LOGISIM_XML.get()
        DOMTree = xml.etree.ElementTree.parse(logisim_xml)
        root = DOMTree.getroot()
        for i in range(rom_num):
            rom = root.findall(".//a[@name='label'][@val='ROM_%d']/../a[@name='contents']" % i)     # ROM组件contents标签的XPath
            if len(rom) != 1:
                messagebox.showinfo("¿", "请确保有且仅有一个ROM_%d" % i)
                return
            rom = rom[0]
            contents = rom.text.split('\n')
            contents[1] = ' '.join(ROMs_contents[i])
            rom.text = '\n'.join(contents)

        DOMTree.write(logisim_xml)

        messagebox.showinfo("！", "应该成功了")


    except xml.etree.ElementTree.ParseError:
        messagebox.showinfo("¿", "请打开靠谱的Logisim .circ文件")
    except FileNotFoundError:
        messagebox.showinfo("¿", "请打开存在的文件")
    finally:
        if f_mars:
            f_mars.close()

tk.Button(window, text="Excute Order", command=run, bg='red', fg='white', font=("Arial Bold", 12)).pack(side='right')   # Excute Order 233

messagebox.showinfo("说明", '请将ROM组件按顺序命名为"ROM_0", "ROM_1", "ROM_2"... 指令高位在前\n请先关闭Logisim再使用本软件\n由于本人近日bug缠身，使用前请备份原文件。 -- Wu23333')
window.mainloop()

