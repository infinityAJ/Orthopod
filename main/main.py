#<imports>
#   <GUI>
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as msg
from PIL import Image, ImageTk
#   </GUI>
#   <models>
import cv2, pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from keras.models import load_model
from keras import backend as keras
#   </models>
#</imports>

#<model-1 alogs>
def resize_and_save(img_name):
    main_image = Image.open(f"images/Fractured Bone/{img_name}")
    x= main_image.resize((310//2, 568//2), Image.NEAREST)
    x.save(f"images/resized/{img_name}")

# passing in a default image name just in case
def calculate(img_name="new.jpg"):
    model_name = "ridge_model"
    # getting resized and original image name with directory
    img_file = 'images/resized/{}'.format(img_name)
    orig_img = 'images/Fractured Bone/{}'.format(img_name)
    # reading images and storing them in variables
    # resizing the image if not resized already
    try:
        img_t = cv2.imread(img_file, cv2.IMREAD_COLOR)
    except:
        resize_n_save(img_file)
    finally:
        img_t = cv2.imread(img_file, cv2.IMREAD_COLOR)
    img = cv2.imread(orig_img, cv2.IMREAD_COLOR)
    # making original image grascale and blurred
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    median = cv2.medianBlur(gray, 5)
    # loading model "ridge_model"
    model = pickle.load(open(model_name,'rb'))
    # calculating predictions using model after flattening out the image into a list
    pred_thresh = int(model.predict(img_t.reshape(1, -1)))
    # creating a black and white image to better understand the fractures
    bool, threshold_img = cv2.threshold(median, pred_thresh, 255, cv2.THRESH_BINARY)
    line = []
    # listing the co-ordinates of beginning and end of white in the picture
    for i in range(0, gray.shape[0]):
        tmp_initial = []
        tmp_final = []
        for j in range(0, gray.shape[1] - 1):
            if threshold_img[i, j] == 0 and (threshold_img[i, j + 1]) == 255:
                tmp_initial.append((i, j))
            if threshold_img[i, j] == 255 and (threshold_img[i, j + 1]) == 0:
                tmp_final.append((i, j))

        x = [each for each in zip(tmp_initial, tmp_final)]
        x.sort(key=lambda each: each[1][1] - each[0][1])
        try:
            line.append(x[len(x) - 1])
        except IndexError:
            pass
    err = 15
    danger_points = []
    dist_list = []
    # finding the thickness of the bone(white in the pic)
    # adding it to danger_points if gap is more than err
    for i in range(1, len(line) - 1):
        dist_list.append(line[i][1][1] - line[i][0][1])
        try:
            prev_ = line[i - 3]
            next_ = line[i + 3]
            dist_prev = prev_[1][1] - prev_[0][1]
            dist_next = next_[1][1] - next_[0][1]
            diff = abs(dist_next - dist_prev)
            if diff > err:
                data = (diff, line[i])
                if len(danger_points):
                    prev_data = danger_points[len(danger_points) - 1]
                    if abs(prev_data[0] - data[0]) > 2 or data[1][0] - prev_data[1][0] != 1:
                        danger_points.append(data)
                else:
                    danger_points.append(data)
        except:
            pass
        start, end = line[i]
        mid = int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)

    # drawing green rectangle around danger points
    for i in range(0, len(danger_points) - 1, 2):
        try:
            start_rect = danger_points[i][1][0][::-1]
            start_rect = (start_rect[0] - 40, start_rect[1] - 40)
            end_rect = danger_points[i + 1][1][1][::-1]
            end_rect = (end_rect[0] + 40, end_rect[1] + 40)
            cv2.rectangle(img, start_rect, end_rect, (0, 255, 0), 2)
        except:
            pass

    #creating figures to show all the calculations and predictions
    fig1, ax1 = plt.subplots(1, 1)
    fig2, ax2 = plt.subplots(1, 1)
    fig3, ax3 = plt.subplots(1, 1)
    x = np.arange(1, gray.shape[0] - 1)
    y = dist_list
    cv2.calcHist(gray, [0], None, [256], [0, 256])
    try:
        ax1.plot(x, y)
    except:
        pass

    # finally returning all the figures AKA output
    img = np.rot90(img)
    ax2.imshow(img)
    ax3.hist(gray.ravel(), 256, [0, 256])
    return (fig2, fig3)
#   </model-1 algos>

# responsible for using the model in a GUI window
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

        self.model = load_model('model.h5', custom_objects={'dice_coef_loss':self.dice_coef_loss, 'dice_coef':self.dice_coef})
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
        Button(self.upload_scr, font=('Verdana',25), text="select the image", command = lambda: self.img_input()).pack(anchor = 'center', pady = 50)
        # ====================================================  output_scr  =====================================
        self.output_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.output_scr.pack_propagate(0)
        # ====================================================  output_scr contents  ============================
        self.mb1 = Button(self.output_scr, font=('Verdana',15), text="model 1", command = lambda: self.switchm(0))
        self.mb1.pack(side=LEFT, anchor=N)
        self.mb2 = Button(self.output_scr, font=('Verdana',15), text="model 2", command = lambda: self.switchm(1))
        self.mb2.pack(side=LEFT, anchor=N)
        # ====================================================  report_scr  =====================================
        self.report_scr = Frame(self.main, width=1000, height=600, bg="#ffffff")
        self.report_scr.pack_propagate(0)

# responsible for splash screen
    def splash(self):
        self.splash.pack_forget()
        self.screen.pack()
        
# called upon clicking the button to upload images
    def img_input(self):
        self.reps += 1
        if self.reps > 1:
            msg.showerror("not allowed", "please restart the application to try with another x-ray file")
            return
        img_path = filedialog.askopenfilename()
        fig1 = self.prepare(img_path)
        fig2, fig3 = calculate(img_path.split('/')[-1])
        img = ImageTk.PhotoImage(Image.open(img_path))
        lbl_img = Label(self.upload_scr, image=img)
        lbl_img.pack()
        lbl_img.image = img
        self.mf1 = FigureCanvasTkAgg(fig1, master=self.output_scr).get_tk_widget()
        self.mf1.pack(anchor=CENTER, pady=10)
        self.mf2 = FigureCanvasTkAgg(fig2, master=self.output_scr).get_tk_widget()
        FigureCanvasTkAgg(fig3, master=self.report_scr).get_tk_widget().pack()

# displays body part selection screen
    def switch_scr1(self):
        self.upload_scr.pack_forget()
        self.output_scr.pack_forget()
        self.report_scr.pack_forget()
        self.in_scr.pack()

# displays upload/input screen
    def switch_scr2(self):
        self.in_scr.pack_forget()
        self.output_scr.pack_forget()
        self.report_scr.pack_forget()
        self.upload_scr.pack()

# displays output screen
    def switch_scr3(self):
        self.upload_scr.pack_forget()
        self.in_scr.pack_forget()
        self.report_scr.pack_forget()
        self.output_scr.pack()

# displays report screen
    def switch_scr4(self):
        self.upload_scr.pack_forget()
        self.output_scr.pack_forget()
        self.in_scr.pack_forget()
        self.report_scr.pack()

# this function is called when we try to switch models in output screen
    def switchm(self, x):
        try:
            if x:
                self.mf1.pack_forget()
                self.mf2.pack(anchor=CENTER, pady=10)
            else:
                self.mf2.pack_forget()
                self.mf1.pack(anchor=CENTER, pady=10)
        except:
            pass

#   <model-2 algos>
    def dice_coef(self, y_true, y_pred):
        y_true_f = keras.flatten(y_true)
        y_pred_f = keras.flatten(y_pred)
        intersection = keras.sum(y_true_f * y_pred_f)
        return (2. * intersection + 1) / (keras.sum(y_true_f) + keras.sum(y_pred_f) + 1)

    def dice_coef_loss(self, y_true, y_pred):
        return -dice_coef(y_true, y_pred)

    def prepare(self, img_path):
        X_shape = 512
        # resizing image to make predictions
        x_im = cv2.resize(cv2.imread(img_path),(X_shape,X_shape))[:,:,0]
        # predicting the fractures
        op = self.model.predict((x_im.reshape(1, 512, 512, 1)-127.0)/127.0)
        # adding image in the prediction
        plt.imshow(x_im, cmap="bone", label="Output Image")
        f = Figure()
        # prepare output
        f.add_subplot(111).imshow(op.reshape(512, 512), alpha=0.5, cmap="jet")
        # return to display output
        return f
#   </model-2 algos>

if __name__ == "__main__":
    root = Tk()
    obj = ortho(root)
    root.mainloop()
#</main>
