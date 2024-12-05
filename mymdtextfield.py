'''
Author: Paoger
Date: 2023-12-08 10:43:27
LastEditors: Paoger
LastEditTime: 2024-01-15 20:14:57
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
#import platform
#pf = platform.system()
#if pf == "Windows":
from kivy.utils import platform
if platform == "win":
    #解决windows下中文输入的候选词显示begin
    import ctypes
    from ctypes import wintypes
    import subprocess

    # windows api 准备
    # GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
    # GlobalLock = ctypes.windll.kernel32.GlobalLock
    GlobalFree = ctypes.windll.kernel32.GlobalFree
    GlobalFree.argtypes = wintypes.HGLOBAL,
    # GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
    # GlobalSize = ctypes.windll.kernel32.GlobalSize
    GlobalLock = ctypes.windll.kernel32.GlobalLock
    GlobalLock.argtypes = wintypes.HGLOBAL,
    GlobalLock.restype = wintypes.LPVOID
    GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
    GlobalUnlock.argtypes = wintypes.HGLOBAL,
    GlobalUnlock.restype = wintypes.BOOL
    GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
    GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
    GlobalAlloc.restype = wintypes.HGLOBAL
    GlobalSize = ctypes.windll.kernel32.GlobalSize
    GlobalSize.argtypes = wintypes.HGLOBAL,
    GlobalSize.restype = ctypes.c_size_t
    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040
    GHND = 0x0042

    class CANDIDATELIST(ctypes.Structure):
       _fields_ = [
           ('dwSize', wintypes.DWORD),
           ('dwStyle', wintypes.DWORD),
           ('dwCount', wintypes.DWORD),
           ('dwSelection', wintypes.DWORD),
           ('dwPageStart', wintypes.DWORD),
           ('dwPageSize', wintypes.DWORD),
           ('dwOffset', ctypes.ARRAY(wintypes.DWORD, 9+1))
           ]
    #解决windows下中文输入的候选词显示end

from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField

from kivy.properties import StringProperty

class MyMDTextField(MDTextField):
    #显示输入词候选的Widget id
    imc_id = StringProperty('imc_id')

    #显示输入词候选的Widget id的Screen id
    imc_scr_id = StringProperty('imc_scr_id')

    def on_imc_id(self, instance, imc_id):
        self.imc_id = imc_id
        #pf = platform.system()
        #if pf == "Windows":
        if platform == "win":
            #绑定输入键盘事件
            self.bind(text=self.ime_press)

    def ime_press(self,*args):
        #pf = platform.system()
        #if pf == "Windows":
        if platform == "win":
            user32 = ctypes.WinDLL(name="user32")
            imm32 = ctypes.WinDLL(name="imm32")
            h_wnd = user32.GetForegroundWindow()
            h_imc = imm32.ImmGetContext(h_wnd)
            # imm32.ImmSetOpenStatus(h_imc, False)
            # mem = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, 30)
            # pcontents = GlobalLock(mem)
            size = imm32.ImmGetCandidateListW(h_imc, 0, None, 0)

            buffer = ctypes.create_string_buffer(size)
            
            ptxt = ctypes.cast(buffer,ctypes.POINTER(CANDIDATELIST))
            imm32.ImmGetCandidateListW.argtypes = (wintypes.HGLOBAL, wintypes.DWORD, ctypes.POINTER(CANDIDATELIST), wintypes.DWORD)
            imm32.ImmGetCandidateListW.restype = ctypes.c_size_t
            imm32.ImmGetCandidateListW(h_imc, 0, ptxt, size)
            
            a = [ptxt.contents.dwOffset[i] for i in range(ptxt.contents.dwPageSize+1)]
            op = [str(ai+1)+':'+str (buffer[a[ai]:a[ai+1]], encoding = 'utf-16') for ai in range(len(a)-1)]

            #print(f"{op=}")

            #竖向候选
            #self.root.ids.outl.text = "\n".join(op)
            #op = ['好','号','好多']
            #横向候选
            my_string = ''
            for item in op:
                my_string += item.replace(' \x00','') + ' '
            
            app = MDApp.get_running_app()
            if self.imc_scr_id:
                app.root.ids[f'{self.imc_scr_id}'].ids[f'{self.imc_id}'].text = my_string
            else:
                app.root.ids[f'{self.imc_id}'].text = my_string
            
            imm32.ImmReleaseContext(h_wnd, h_imc)
        else:
            pass

    def __init__(self, **kwargs):
        super(MyMDTextField, self).__init__(**kwargs)
        """ pf = platform.system()
        if pf == "Windows":
            #绑定输入键盘事件
            self.bind(text=self.ime_press) """
    
