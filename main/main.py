from tkinter import *
from tkinter import filedialog
import random
from tkinter import messagebox as msg
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculate import Calculate


class ortho:
    def __init__(self, root):
        # ====================================================  root window  ====================================
        self.root = root
        self.root.geometry('1350x700+0+0')
        self.root.title('OrthoPod')
        self.root.resizable(0, 0)
        self.root.after(1000, self.splash)
        self.reps = 0
        # ====================================================  variables  ======================================
        self.options = [
            "head",
            "shoulder",
            "ribs",
            "back",
            "waist",
            "thighs",
            "legs",
            "feet"
        ]

        self.plasters = [
            "Plaster Cast",
            "Synthetic Cast",
            "Cast Brace",
            "Splint/ Half Cast"
        ]

        self.img_path = ""
        self.chosen = StringVar()
        self.chosen.set('Select')
        self.logo = PhotoImage(file="ortho.png").subsample(7, 7)
        root.iconphoto(False, self.logo)
        self.human = PhotoImage(file="human.png").subsample(1, 1)
        # ====================================================  splash screen  ==================================
        self.splash_view = PhotoImage(file="splash.png")
        self.splash = Frame(self.root, width=1350, height=700)
        self.splash.pack()
        self.splash_screen = Label(self.splash, image=self.splash_view)
        self.splash_screen.pack()
        # ====================================================  root screen  ====================================
        Label(self.root, bg="#100e3f", fg="#ffffff", width=1350, image=self.logo, anchor='nw', compound=LEFT,
              text="  OrthoPod", font=('Verdana', 30, 'bold')).pack(side=TOP)
        self.screen = Frame(self.root, bg="#ffffff", width=1350, height=600)
        self.menu = Frame(self.screen, width=350, height=600, bg="#eeeeee")
        self.menu.pack(side=LEFT)
        self.menu.pack_propagate(0)
        self.main = Frame(self.screen, width=1000, height=600, bg="#000022")
        self.main.pack(side=RIGHT)
        self.main.pack_propagate(0)
        # ====================================================  navigation menu  ================================
        Button(self.menu, bg="#ffffff", font=('Verdana', 20, 'bold'), text="body part selection",
               command=lambda: self.switch_scr1()).pack(fill=X, pady=10)
        Button(self.menu, bg="#ffffff", font=('Verdana', 20, 'bold'), text="upload X-ray",
               command=lambda: self.switch_scr2()).pack(fill=X, pady=10)
        Button(self.menu, bg="#ffffff", font=('Verdana', 20, 'bold'), text="output",
               command=lambda: self.switch_scr3()).pack(fill=X, pady=10)
        Button(self.menu, bg="#ffffff", font=('Verdana', 20, 'bold'), text="report",
               command=lambda: self.switch_scr4()).pack(fill=X, pady=10)
        # ========================================  in_scr  =============================(the frame that gets replaced)
        self.in_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.in_scr.pack()
        self.in_scr.pack_propagate(0)
        # ====================================================  in_scr contents  ================================
        self.opt = OptionMenu(self.in_scr, self.chosen, *self.options)
        self.opt.config(width=10, font=('Verdana', 20))
        self.opt['menu'].config(font=('Verdana', 15))
        self.opt.pack(side=LEFT, anchor='n', padx=250, pady=30)
        Label(self.in_scr, height=600, image=self.human, bg="#ffffff").pack(side=RIGHT)
        # ====================================================  upload_scr  =====================================
        self.upload_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.upload_scr.pack_propagate(0)
        # ====================================================  upload_scr contents  ============================
        Button(self.upload_scr, font=('Verdana', 25), text="select the image", command=lambda: self.img_input()).pack(
            anchor='center', pady=50)
        # ====================================================  output_scr  =====================================
        self.output_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.output_scr.pack_propagate(0)
        # ====================================================  output_scr contents  ============================
        self.output_info = Label(self.output_scr, background="#ffffff", font=('Verdana', 10),
                                 text="no file selected yet")
        self.output_info.pack(pady=100, anchor='center')
        # ====================================================  report_scr  =====================================
        self.report_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.report_scr.pack_propagate(0)

    def splash(self):
        self.splash.pack_forget()
        self.screen.pack()

    def img_input(self):
        self.reps += 1
        if self.reps > 1:
            msg.showerror("not allowed", "please restart the application to try with another x-ray file")
            root.destroy()
            return
        self.img_path = filedialog.askopenfilename()
        calc = Calculate(self.img_path.split("/")[-1])
        img = ImageTk.PhotoImage(Image.open(self.img_path))
        render = Label(self.upload_scr, image=img)
        render.image = img
        render.pack()
        self.output_info.pack_forget()
        FigureCanvasTkAgg(calc.fig2, master=self.output_scr).get_tk_widget().pack()
        FigureCanvasTkAgg(calc.fig3, master=self.report_scr).get_tk_widget().pack()
        Label(self.report_scr, background="#ffffff", font=('Verdana', 15, 'bold'),
              text="Suggested Cast Treatment: " + random.choice(self.plasters)).pack()

    def switch_scr1(self):
        self.upload_scr.pack_forget()
        self.output_scr.pack_forget()
        self.report_scr.pack_forget()
        self.in_scr.pack()

    def switch_scr2(self):
        self.in_scr.pack_forget()
        self.output_scr.pack_forget()
        self.report_scr.pack_forget()
        self.upload_scr.pack()

    def switch_scr3(self):
        self.upload_scr.pack_forget()
        self.in_scr.pack_forget()
        self.report_scr.pack_forget()
        self.output_scr.pack()

    def switch_scr4(self):
        self.upload_scr.pack_forget()
        self.output_scr.pack_forget()
        self.in_scr.pack_forget()
        self.report_scr.pack()


if __name__ == "__main__":
    root = Tk()
    obj = ortho(root)
    root.mainloop()
