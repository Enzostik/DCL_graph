### Por https://github.com/Enzostik.

from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DCL import Line, LineData, GraphData, construct
from file_functions import get_dirname

#load dirname
app_dirname = get_dirname(__file__)
file_dirname = None

fileChanged = False
SupportOptions = ["0. NINGUNO", "1. FIJO", "2. DESLIZANTE", "3. EMPOTRAMIENTO_L", "4. EMPOTRAMIENTO_R"]

Points_dataframe:pd.DataFrame = pd.DataFrame({'name': pd.Series(dtype='str'),
                                              'position': pd.Series(dtype='float'),
                                              'supportType': pd.Series(dtype='int'),
                                              "xLoad": pd.Series(dtype='float'),
                                              'yLoad': pd.Series(dtype='float'),
                                              'Mf': pd.Series(dtype='float'),
                                              'Mt': pd.Series(dtype='float'),
                                              'izq/der': pd.Series(dtype='bool'),
                                              'Mf_der': pd.Series(dtype='float'),
                                              'Mt_der': pd.Series(dtype='float')
                                              })

def new_dataframe_info():
    global Points_dataframe, file_dirname
    Points_dataframe = Points_dataframe[0:0]
    file_dirname = ''

def load_dataframe_info() -> bool:
    global Points_dataframe, file_dirname, fileChanged
    file_dirname = filedialog.askopenfilenames(filetypes=[('CSV File', '*.csv'),('EXCEL File', '*.xlsx')], defaultextension = [('CSV File', '*.csv')])
    if not file_dirname:
        return False
    file_dirname = file_dirname[0]
    if file_dirname.split('.')[-1] == "csv":
        Points_dataframe = pd.read_csv(file_dirname)
    elif file_dirname.split('.')[-1] == "xlsx":
        Points_dataframe = pd.read_excel(file_dirname)
    fileChanged = False
    return True

def save_dataframe_info() -> bool:
    global fileChanged, file_dirname
    if not file_dirname:
        file_dirname = filedialog.asksaveasfilename(filetypes=[('CSV File', '*.csv'),('EXCEL File', '*.xlsx')], defaultextension = [('CSV File', '*.csv')])
    if not file_dirname:
        return False
    by_position_points = Points_dataframe.sort_values(by=['position'], ascending=True)
    if file_dirname.split('.')[-1] == "csv":
        by_position_points.to_csv(file_dirname, index=False)
    elif file_dirname.split('.')[-1] == "xlsx":
        by_position_points.to_excel(file_dirname, index=False)
    fileChanged = False
    return True

def check_save(title:str = "Guardar", msg:str = "¿Desea guardar el archivo?") -> bool:
    if fileChanged:
        question = messagebox.askyesnocancel(title, msg)
        if question == True:
            return save_dataframe_info()
        elif question == None:
            return False
    return True

def check_pname(name:str)->str:
    if name != "" and name != " ":
        return name
    return "null"

def construct_image():
    savefile_dirname= filedialog.asksaveasfilename(filetypes=[('PNG', '*.png'),('JPG','*.jpg')], defaultextension = [('PNG', '*.png')])
    if not savefile_dirname:
        return
    graph_data = GraphData("Diagrama de cuerpo libre", "Posición", "mm")
    solicitaciones = LineData(
                'Solicitaciones',
                'kgf',
                'blue',
                width = 1.5,
                linetype = Line.ARROW)
    flector = LineData(
                'Momento flector',
                'kgf.cm',
                'red',
                width = 1.5,
                linetype = Line.FLINE,
                invert = True)
    torsor = LineData(
                'Momento torsor',
                'kgf.cm',
                'green',
                width = 1.5,
                linetype = Line.FLINE)
    
    by_position_points = Points_dataframe.sort_values(by=['position'], ascending=True)
    for index, row in by_position_points.iterrows():
        graph_data.add_point(index, row['name'])
        #Cargar las solicitaciones
        solicitaciones.add_points([(float(row['position']), 0)])
        new_value = [[float(row['xLoad']), float(row['yLoad']), int(row['supportType']), index]]
        if len(solicitaciones.values) == 0:
            solicitaciones.values = new_value
        else:
            solicitaciones.values =np.concatenate([solicitaciones.values, np.array(new_value)])
        #Cargar los momentos flectores
        flector.add_points([(float(row['position']), float(row['Mf']))])
        #Cargar los momentos flectores
        torsor.add_points([(float(row['position']), float(row['Mt']))])
        if row['izq/der']:
            #Cargar los momentos flectores a la derecha
            flector.add_points([(float(row['position']), float(row['Mf_der']))])
            #Cargar los momentos flectores a la derecha
            torsor.add_points([(float(row['position']), float(row['Mt_der']))])
    #Cargar los datos de los puntos
    graph_data.load_y_dict({
        0:  solicitaciones,
        1:  flector,
        2:  torsor
    })
    #construir la imágen y guardarla
    construct(graph_data, savefile_dirname)

class Point_UI:
    def __init__(self, wnd):
        #Elementos
        label1 = Label(wnd, text="Nombre")
        self.entry_name=Entry(wnd, width=25)
        label2 = Label(wnd, text="Posición [mm]")
        self.position=Entry(wnd, width=25)
        label3 = Label(wnd, text="Tipo de soporte")
        self.value_supportType = StringVar(wnd)
        entry_supportType=OptionMenu(wnd, self.value_supportType, *SupportOptions)
        label4 = Label(wnd, text="Carga X [kgf]")
        self.entry_xLoad=Entry(wnd, width=25)
        label5 = Label(wnd, text="Carga Y [kgf]")
        self.entry_yLoad=Entry(wnd, width=25)
        label6 = Label(wnd, text="Momento Flector [kgf.cm]")
        self.entry_Mf=Entry(wnd, width=25)
        label7 = Label(wnd, text="Momento Torsor [kgf.cm]")
        self.entry_Mt=Entry(wnd, width=25)
        self.checkbox_variable = BooleanVar(wnd)
        checkbox = Checkbutton(wnd, text="Derecha/Izquierda", variable=self.checkbox_variable,command=self.check_clicked)
        label8 = Label(wnd, text="Momento Flector der. [kgf.cm]")
        self.entry_Mf_der=Entry(wnd, width=25, state="disabled")
        label9 = Label(wnd, text="Momento Torsor der. [kgf.cm]")
        self.entry_Mt_der=Entry(wnd, width=25, state="disabled")
        
        #Configurar para validar las entradas tipo flotante
        reg_name = wnd.register(self.validate_string)
        reg = wnd.register(self.validate_float)
        self.entry_name.config(validate='key', validatecommand=(reg_name, '%P'))
        self.position.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_xLoad.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_yLoad.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_Mf.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_Mt.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_Mf_der.config(validate='key', validatecommand=(reg, '%P'))
        self.entry_Mt_der.config(validate='key', validatecommand=(reg, '%P'))

        #Pack in frame
        label1.grid(row=0, column=0, sticky="w")
        self.entry_name.grid(row=0, column=1)
        label2.grid(row=1, column=0, sticky="w")
        self.position.grid(row=1, column=1)
        label3.grid(row=2, column=0, sticky="w")
        entry_supportType.grid(row=2, column=1, sticky="nsew")
        label4.grid(row=3, column=0, sticky="w")
        self.entry_xLoad.grid(row=3, column=1)
        label5.grid(row=4, column=0, sticky="w")
        self.entry_yLoad.grid(row=4, column=1)
        label6.grid(row=5, column=0, sticky="w")
        self.entry_Mf.grid(row=5, column=1)
        label7.grid(row=6, column=0, sticky="w")
        self.entry_Mt.grid(row=6, column=1)
        checkbox.grid(row=7, sticky="w")
        label8.grid(row=8, column=0, sticky="w")
        self.entry_Mf_der.grid(row=8, column=1)
        label9.grid(row=9, column=0, sticky="w")
        self.entry_Mt_der.grid(row=9, column=1)

    def validate_float(self, input):
        if " " in input:
            return False
        if input != "":
            try:
                float(input)
            except:
                return False
        return True
    
    def validate_string(self, input):
        if " " in input:
            return False
        return True
        
    def check_clicked(self, event=None):
        if self.checkbox_variable.get():
            value = "normal"
        else:
            value = "disabled"
        self.entry_Mf_der.config(state=value)
        self.entry_Mt_der.config(state=value)

    def load_from_dict(self, key:int):
            value = Points_dataframe.iloc[key]
            #Cambiar los valores en las entradas
            self.entry_name.delete(0, END)
            self.entry_name.insert(0, value['name'])
            
            self.position.delete(0, END)
            self.position.insert(0, value['position'])

            self.value_supportType.set(SupportOptions[int(value['supportType'])])
            
            self.entry_xLoad.delete(0, END)
            self.entry_xLoad.insert(0, value['xLoad'])
            
            self.entry_yLoad.delete(0, END)
            self.entry_yLoad.insert(0, value['yLoad'])
            
            self.entry_Mf.delete(0, END)
            self.entry_Mf.insert(0, value['Mf'])
            
            self.entry_Mt.delete(0, END)
            self.entry_Mt.insert(0, value['Mt'])

            self.checkbox_variable.set(bool(value['izq/der']))
            
            self.entry_Mf_der.config(state='normal')
            self.entry_Mf_der.delete(0, END)
            self.entry_Mf_der.insert(0, value['Mf_der'])
            
            self.entry_Mt_der.config(state='normal')
            self.entry_Mt_der.delete(0, END)
            self.entry_Mt_der.insert(0, value['Mt_der'])
            
            self.check_clicked()

    def update_dict(self, key:int) -> str:
        name = lambda x: x if x!="" else " "
        value = lambda x: 0 if x=="" else x
        #Modificar informacion del diccionario
        Points_dataframe.iloc[key] = [
            name(self.entry_name.get()),
            float(value(self.position.get())),
            int(self.value_supportType.get()[0]),
            float(value(self.entry_xLoad.get())),
            float(value(self.entry_yLoad.get())),
            float(value(self.entry_Mf.get())),
            float(value(self.entry_Mt.get())),
            bool(self.checkbox_variable.get()),
            float(value(self.entry_Mf_der.get())),
            float(value(self.entry_Mt_der.get()))
        ]
        #Devolver el nombre para actualizar la lista
        return check_pname(self.entry_name.get())
        # if name(self.entry_name.get()) == " ":
        #     return "null"
        # return self.entry_name.get()

class UI:
    def __init__(self, wnd):
        #Frame de la ventana
        self.window = wnd
        #Barra de menú principal
        menus_bar = Menu()
        #Menú de archivos
        file_menu = Menu(menus_bar, tearoff=False)
        file_menu.add_command(
            label="Nuevo",
            accelerator="Ctrl+N",
            command=self.new_data
        )
        file_menu.add_command(
            label="Abrir",
            accelerator="Ctrl+O",
            command=self.load_data
        )
        file_menu.add_command(
            label="Guardar",
            accelerator="Ctrl+S",
            command=self.save_data
        )
        file_menu.add_command(
            label="Guardar como",
            accelerator="Ctrl+Shift+S",
            command=self.save_as_data
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Salir",
            command=lambda x=wnd : x.destroy() if check_save("Salir", "¿Desea guardar el archivo antes de salir?") else None
        )
        #Menú de imágen
        image_menu = Menu(menus_bar, tearoff=False)
        image_menu.add_command(
            label="DCL",
            accelerator="Ctrl+Enter",
            command=self.generate_DCL
        )

        #Añadir menú de archivos
        menus_bar.add_cascade(menu=file_menu, label="Archivo")
        menus_bar.add_cascade(menu=image_menu, label="Imágen")

        #Generar los elementos
        label1=Label(master=wnd,text="Añadir los puntos del diagrama")
        scrollbar = Scrollbar(master=wnd, orient=VERTICAL)
        self.list_points = Listbox(master=wnd, exportselection=False, yscrollcommand=scrollbar.set)
        but_add = Button(master=wnd, text="Añadir punto", width=25, command=self.add_point)
        but_remove = Button(master=wnd, text="Quitar punto", width=25, command=self.remove_point)
        but_generate = Button(master=wnd, text="Generar diagrama", width=25, command=self.generate_DCL)
        but_update = Button(wnd, text="Actualizar", width = 15, command = self.update_point)
        #configurar scrollbar
        scrollbar.config(command=self.list_points.yview)
        #Parámetros del punto
        frame1 = Frame(wnd, width=100, height=250)
        self.point_info = Point_UI(frame1)
        self.list_points.bind("<<ListboxSelect>>", self.on_selected_point)
        
        #Asociar atajos
        wnd.bind_all("<Control-a>", self.add_point)
        wnd.bind_all("<Control-d>", self.remove_point)
        wnd.bind_all("<Control-n>", self.new_data)
        wnd.bind_all("<Control-o>", self.load_data)
        wnd.bind_all("<Control-s>", self.save_data)
        wnd.bind_all("<Control-Shift-s>", self.save_data)
        wnd.bind_all("<Control-Return>", self.generate_DCL)
        #Insertar/Ubicar los elementos
        wnd.config(menu=menus_bar)

        label1.grid(row=0, column=1, columnspan=3)
        self.list_points.grid(row=1, column=0, columnspan=2, sticky="nswe")
        scrollbar.grid(row=1, column=2, sticky="nswe")
        frame1.grid(row=1,column=3, sticky="nswe")
        but_add.grid(row=3, column=0, sticky="e")
        but_remove.grid(row=3, column=1, sticky="e")
        but_update.grid(row=3, column=3)
        but_generate.grid(row=0, column=0, columnspan=2)

    def add_point(self, event=None):
        #Añadir nuevo elemento al diccionario
        global Points_dataframe, fileChanged
        Points_dataframe = pd.concat([Points_dataframe, pd.DataFrame({
            'name':['Nuevo Punto'],
            'position' : [0.0],
            'supportType' : [0],
            'xLoad': [0.0],
            'yLoad': [0.0],
            'Mf': [0.0],
            'Mt': [0.0],
            'izq/der': [False],
            'Mf_der': [0.0],
            'Mt_der': [0.0]
        })], ignore_index=True)
        #Agregar nombre en la lista
        self.list_points.insert(END, f"- Nuevo Punto")
        #Indicar que se han hecho cambios
        fileChanged = True
    
    def on_selected_point(self, event=None):
        selected = self.list_points.curselection()
        if selected:
            self.point_info.load_from_dict(selected[0])
    
    def remove_point(self, event=None):
        selected = self.list_points.curselection()
        if selected:
            global Points_dataframe, fileChanged
            self.list_points.delete(selected)
            Points_dataframe = Points_dataframe.drop(Points_dataframe.index[selected[0]])
            #Indicar que se han hecho cambios
            fileChanged = True

    def generate_DCL(self, event=None):
        if self.list_points.size() == 0:
            return
        construct_image()

    def update_point(self, event=None):
        selected = self.list_points.curselection()
        if selected:
            global fileChanged
            #Actualizar diccionario
            name = self.point_info.update_dict(selected[0])
            #Actualizar nombre en la lista
            self.list_points.delete(selected)
            self.list_points.insert(selected, f"- {name}")
            #Indicar que se han hecho cambios
            fileChanged = True

    def save_data(self, event=None):
        save_dataframe_info()
    
    def save_as_data(self, event=None):
        global file_dirname
        file_dirname = ""
        save_dataframe_info()
    
    def new_data(self, event=None):
        if check_save():
            new_dataframe_info()
            #Borrar todos los puntos en la lista
            self.list_points.delete(0, END)

    def load_data(self, event=None):
        if check_save():
            if not load_dataframe_info():
                return
            #Limpiar los puntos de la lista y cargar los que se encuentran en el archivo
            self.list_points.delete(0, END)
            for _index, row in Points_dataframe.iterrows():
                self.list_points.insert(END, f"- {check_pname(row['name'])}")
            #Cambiar el nombre del encabezado
            self.window.title(f"Diagrama de Cuerpo Libre - {file_dirname.split('/')[-1]}")

def main():
    window = Tk()
    window.title("Diagrama de Cuerpo Libre")
    window.resizable(False, False)
    UI(window)

    window.protocol("WM_DELETE_WINDOW", lambda x=window : x.destroy() if check_save("Salir", "¿Desea guardar el archivo antes de salir?") else None)
    window.mainloop()

if __name__=="__main__":
    main()
