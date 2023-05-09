import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import sympy as sy
from sympy.parsing.sympy_parser import *
import numpy as np
from PIL import ImageTk, Image
from mpl_toolkits.axisartist.axislines import AxesZero


a = 0
b = 0
color = 'Blue'
[lower, upper] = [-500, 500]
x = sy.Symbol('x')

#Main Window
win = tk.Tk()
win.geometry("1920x1080")
win.title("Graph Calculator")

#Label Widget
label = ttk.Label(win, text="Enter the function F(x)")
label.config(font=('Product Sans', 18))
label.grid(column=0, row=0, sticky='NW', pady=15, padx=45)

#Entry WIdget
fn = tk.StringVar()
fn_entered = ttk.Entry(win, width=40, textvariable=fn)
fn_entered.grid(column=0, row=1, sticky='NW', pady=15, padx=10, ipady=5)
fn_entered.config(font=('Product Sans', 10))
fn_entered.focus()

#Canvas widget
img_canvas = tk.Canvas(win, width=0, height=0)
img_canvas.grid(column=0, row=0, sticky='NW', ipady=20, ipadx=20, pady=7)

#ImageTk in Canvas
img = ImageTk.PhotoImage(Image.open("blue.png"))
img_alert = ImageTk.PhotoImage(Image.open("blue_alert.png"))
curve_img = ImageTk.PhotoImage(Image.open("blue_curve.png"))
img_canvas.create_image(20, 25, image=img)

#Figure Widget for Plot
fig = Figure(figsize=(10, 10), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=win)


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, ax, base_scale=2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location

            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)

        return onMotion


def make_graph():
    global fig, canvas
    fig = Figure(figsize=(10, 8), dpi=100)
    #Subplot
    graph = fig.add_subplot(111, xlim=(-10, 10), ylim=(-5, 5), autoscale_on=False, axes_class=AxesZero)
    graph.grid(linestyle='--')
    for direction in ["xzero", "yzero"]:
        graph.axis[direction].set_axisline_style("-|>")
        graph.axis[direction].set_visible(True)
    #plt.plot()
    graph.plot(a, b, color=color)
    graph.set_xlabel("X")
    graph.set_ylabel("Y")
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().grid(column=3, row=0, rowspan=5, sticky='E')
    toolbar = NavigationToolbar2Tk(canvas, win, pack_toolbar=False)
    canvas.draw()
    toolbar.update()
    scale = 1.1
    zp = ZoomPan()
    figZoom = zp.zoom_factory(graph, base_scale=scale)
    figpan = zp.pan_factory(graph)


def click_me_event(event=None):
    global a, b, lower, upper
    expr = fn_entered.get().lower()
    expr = expr.replace(' ', '').replace('e', str(np.exp(1))).replace('|x|', 'abs(x)')
    if 'log(x)' in expr or '^(1/2)' in expr:
        lower = 10**-100
    else:
        lower = -500
        upper = 500
    if 'asin(x)' in expr or 'acos(x)' in expr:
        lower = -1
        upper = 1
    else:
        if lower > 0:
            pass
        else:
            lower = -500
            upper = 500

    try:
        func = parse_expr(expr, transformations='all')
        f = sy.lambdify(x, func, "numpy")
        a = np.arange(lower, upper, 0.1)
        b = f(a)
        img_canvas.create_image(21, 22, image=curve_img)
        make_graph()
    except:
        img_canvas.create_image(20, 22, image=img_alert)
    finally:
        fn_entered.update()
        fn_entered.focus()


def change_color():
    global color
    color_code = colorchooser.askcolor(title="Choose Line Color")
    if color_code[1] != 'None':
        color = color_code[1]
    else:
        color = color
    make_graph()


def do_nothing(event):
    pass


def save():
    fig.savefig('Plot.png')
    save_button.config(text='Plot Saved Successfully!')


special_keys = ['<Shift_L>', '<Shift_R>', '<Control_L>', '<Control_R>', '<Caps_Lock>', '<Alt_L>', '<Alt_R>',
                '<Escape>', '<Tab>', '<Up>', '<Down>', '<Right>', '<Left>']

for keys in special_keys:
    win.bind(keys, do_nothing)
else:
    win.bind('<Key>', click_me_event)

color_button = ttk.Button(win, text='Select Line Color', command=change_color, width=20)
color_button.grid(column=0, row=2)
save_button = ttk.Button(win, text='Save Plot', command=save, width=20)
save_button.grid(column=0, row=3)
make_graph()

win.mainloop()
