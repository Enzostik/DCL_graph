### Por https://github.com/Enzostik.

#Diagrama de Cuerpo Libre: Para vigas
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
import numpy as np
from file_functions import get_dirname

# sys.path.append('..')
# from mis_modulos import file_functions as ff_

dirname = get_dirname(__file__)
# ff_.check_dir(dirname+'/graphs')

#Configuration
FILL_AREAS = True
FILL_ALPHA = 0.5
FONTSIZE1 = 10
FONTSIZE2 = 8

#Data
class Line:
    LINE, VLINE, FLINE, ARROW = 0, 1, 2, 3

class Support:
    NULL, FIJO, DESLIZANTE, EMPOTRAMIENTO_L, EMPOTRAMIENTO_R = 0, 1, 2, 3, 4

class LineData:
    def __init__(self, name:str, unit:str, color:str, width:float = 1.0, linetype:int = Line.LINE, invert:bool = False, points:list[tuple[float, float]] = [()], values:list = []):
        self.name = name
        self.unit = unit
        self.color = color
        self.width = width
        self.linetype = linetype
        self.invert = invert
        self.x = []
        self.y = []
        self.values = np.array(values)

        #Si hay puntos cargados actualizar los elementos X e Y
        if len(points) > 1:
            self.add_points(points)
    
    def add_points(self, points:list[tuple[float, float]]):
        for p in points:
            self.x.append(p[0])
            self.y.append(p[1])
    
    def get_points(self):
        return zip(self.x, self.y)


class GraphData:
    def __init__(self, name:str, xname:str = "x", xunit:str = "", points_names:dict = {}):
        self.name = name
        self.xaxis_name = xname
        self.xaxis_unit = xunit
        self.yaxis_dict = {}
        self.points_names = points_names
    
    def define_line(self, pos:int, line:LineData):
        self.yaxis_dict[pos] = line

    def load_y_dict(self, lines:dict[int,LineData]):
        self.yaxis_dict = lines

    def get_xaxis_label(self):
        return f"{self.xaxis_name} [{self.xaxis_unit}]"
    
    def get_axis_info(self, i:int):
        _a = self.yaxis_dict[i]
        return f"{_a.name} [{_a.unit}]", _a.color
    
    def add_point(self, index, name):
        self.points_names[index] = name
    
    def define_points(self, names:list[str]):
        self.points_names.clear()
        for i, n in enumerate(names):
            self.points_names[i] = n

def create_Yaxis(axis:plt.Axes, name:str, color:str, fontsize = 10):
    #name, color = get_values(i)
    #Nombrar la etiqueta
    axis.set_ylabel(name, fontsize = fontsize)
    #Cambiar el color de la etiqueta
    axis.yaxis.label.set_color(color)
    #Cambiar el color de los ticks
    axis.tick_params(axis='y', colors=color)

def set_bound_value(axis:plt.Axes, invert = False):
    low, high = axis.get_ylim()
    bound = max(abs(low), abs(high))
    if invert:  bound = -bound
    axis.set_ylim(-bound, bound)

#Vertical line
def draw_vlines(axis:plt.Axes, info:LineData):
    axis.vlines(info.x, ymin = 0, ymax = info.y, colors = info.color, linewidth = info.width)

#Filled line
def draw_lines(axis:plt.Axes, info:LineData):
    axis.plot(info.x, info.y, info.color, linewidth = info.width)

def draw_flines(axis:plt.Axes, info:LineData):
    axis.plot(info.x, info.y, info.color, linewidth = info.width)
    if FILL_AREAS:
        axis.fill_between(info.x, info.y, color = 'none', alpha = FILL_ALPHA, hatch='||', edgecolor = info.color)

def draw_arrow(axis:plt.Axes, info:LineData, graph_data:GraphData):
    #Pasar a ver los apoyos y cargas
    vectors = info.values
    for v0, v1 in zip(info.get_points(), vectors):
        #Colocar los iconos de los apoyos
        val = 0
        match v1[2]:
            case Support.NULL:
                pass
            case Support.FIJO:
                val = "apoyo_fijo"
            case Support.DESLIZANTE:
                val = "apoyo_deslizante"
            case Support.EMPOTRAMIENTO_L:
                val = "empotramiento_L"
            case Support.EMPOTRAMIENTO_R:
                val = "empotramiento_R"
        if val != 0:
            try:
                img = plt.imread(f'{dirname}/resources/{val}.png')
            except TypeError:
                pass
            im = OffsetImage(img, zoom = 0.25)
            ab = AnnotationBbox(im, v0, xycoords='data', frameon=False)
            axis.add_artist(ab)
        #Dibujar las flechas
        axis.quiver(v0[0],
                    v0[1],
                    v1[0],
                    0,
                    scale = 2,
                    scale_units='y',
                    color = 'blue',
                    width=0.005,
                    zorder=10)
        axis.quiver(v0[0],
                    v0[1],
                    0,
                    v1[1],
                    scale = 1,
                    scale_units='y',
                    color = 'blue',
                    width=0.005,
                    zorder=10)
        #Agregar anotación del punto
        axis.annotate(graph_data.points_names[v1[3]], (v0[0]+5,v0[1]+15))
    #Cambiar los límites para que entre todo el gráfico
    axis.set_ylim((-1, max(abs(vectors[:,1].min()), abs(vectors[:,1].max()))+50))
    
    #Dibujar línea del cuerpo del elemento
    axis.plot((info.x[0],info.x[-1]), (info.y[0],info.y[-1]), 'black', linewidth = 2.5)


#General draw function
def draw_plot(axis:plt.Axes, info:LineData, graph_data:GraphData = None):
    match info.linetype:
        case Line.LINE:
            axis.plot(info.x, info.y, info.color, linewidth = info.width)
        case Line.FLINE:
            draw_flines(axis, info)
        case Line.VLINE:
            draw_vlines(axis, info)
        case Line.ARROW:
            draw_arrow(axis, info, graph_data)

def construct(data:GraphData, save_directory:str):
    n_axxs = len(data.yaxis_dict)
    fig, axis1 = plt.subplots(figsize=(8,6))
    fig.subplots_adjust(left = 0.15, right=0.75, top=0.95, bottom=0.085)

    #Crear los ejes Y adicionales
    for i in range(n_axxs - 1):
        axis1.twinx()

    #Configurar el eje X
    axis1.set_xlabel(data.get_xaxis_label())

    #Configurar los ejes Y de la figura
    for i, axxs in enumerate(list(fig.axes)):
        line = data.yaxis_dict[i]
        axis_name, axis_color = data.get_axis_info(i)
        #Configurar la posición de los ejes: Mover las etiquetas y ejes a la derecha
        if i>0: axxs.spines["right"].set_position(("axes", 1.0+(i-1)*0.25))
        #Configurar el nombre y color de los ejes Y
        create_Yaxis(axxs, axis_name, axis_color, fontsize = FONTSIZE1)
        #Cargar los valores x, y del diccionario
        draw_plot(axxs, line, data)
        #Volver simétricos los ejes Y con el orígen
        set_bound_value(axxs, line.invert)

    #Solo visualizar una de las rejillas para que no se superpongan
    axis1.grid(axis='x')

    #Que axis1 siempre esté en el frente
    axis1.set_zorder(10)
    axis1.patch.set_visible(False)

    #Dibujar una línea negra en el orígen de Y
    plt.axhline(0, color = 'black', linewidth = 0.5)

    #Visualizar en diagramas separados
    fig2, axs2 = plt.subplots(n_axxs,figsize=(6,10))
    fig2.subplots_adjust(left = 0.15, right=0.95, top=0.95, bottom=0.085, hspace=0)
    #Configurar los ejes X
    for i, axxs in enumerate(list(axs2)):
        line = data.yaxis_dict[i]
        axis_name, axis_color = data.get_axis_info(i)
        if i == n_axxs - 1:
            axxs.set_xlabel(data.get_xaxis_label())
        create_Yaxis(axxs, axis_name, axis_color, fontsize = FONTSIZE2)
        draw_plot(axxs, line, data)
        set_bound_value(axxs, line.invert)
        axxs.set_xlim(axis1.get_xlim())
        axxs.axhline(0, color = 'black', linewidth = 0.5)
        axxs.grid(axis='x')
    fig2.align_ylabels(axs2)

    #Guardar como .png
    #fig.savefig(save_directory+'/All_DCL.png')
    fig2.savefig(save_directory)
    # fig.show()
    # fig2.show()
    plt.close("all")

#graph_data = GraphData("Diagrama de cuerpo libre", "Posición", "mm")
# graph_data.define_points(["", "A", "B", "C1", "C2"])
# graph_data.load_y_dict({
#     0:  LineData(
#             'Solicitaciones',
#             'kgf',
#             'blue',
#             width = 1.5,
#             linetype = Line.ARROW,
#             points = [
#                 (0, 0),
#                 (30, 0),
#                 (67.5, 0),
#                 (162.5,0),
#                 (200,0),
#                 (245,0)
#             ],
#             values= [
#                 [0, 0, Support.NULL, 0],
#                 [0, 1280.72, Support.EMPOTRAMIENTO_L, 1],
#                 [0, -1280.72, Support.NULL, 3],
#                 [0, -1280.72, Support.NULL, 4],
#                 [0, 1280.72, Support.EMPOTRAMIENTO_R, 2],
#                 [0, 0, Support.NULL, 0]
#             ]),

#     1:  LineData(
#             'Momento flector',
#             'kgf.cm',
#             'red',
#             width = 1.5,
#             linetype = Line.FLINE,
#             invert = True,
#             points = [
#                 (30, 0),
#                 (30, -3743.28),
#                 (67.5, 1059.42),
#                 (162.5, 1059.42),
#                 (200,-3743.28),
#                 (200,0)
#             ]),

#     2:  LineData(
#             'Momento torsor',
#             'kgf.cm',
#             'green',
#             width = 1.5,
#             linetype = Line.FLINE,
#             points = [
#                 (0, 0)
#             ]),
# })

# construct(graph_data, dirname+'/graphs/Individual_DCL.png'')