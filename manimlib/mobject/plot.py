import itertools as it
from manimlib.constants import *
from manimlib.mobject.functions import ParametricFunction
from manimlib.mobject.geometry import Dot
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.number_line import NumberLine
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_gradient
from manimlib.utils.bezier import interpolate

#from manimlib.mobject.svg.brace import Brace
#from manimlib.utils.iterables import tuplify


class Plot(VGroup):
    CONFIG = {
        #"height": 4,
        #"width": 6,
        #"n_ticks": 4,
        #"tick_width": 0.2,
        #"label_y_axis": True,
        #"y_axis_label_height": 0.25,
        #"max_value": 1,
        #"bar_colors": [BLUE, YELLOW],
        #"bar_fill_opacity": 0.8,
        #"bar_stroke_width": 3,
        #"bar_names": [],
        #"bar_label_scale_val": 0.75,
        
        "x_min": -1,
        "x_max": 10,
        "x_axis_width": 9,
        "x_tick_frequency": 1,
        "x_leftmost_tick": None,  # Change if different from x_min
        "x_labeled_nums": None,
        "x_elongated_nums": None,
        "x_axis_label": "$x$",
        "x_axis_label_position": UR,
        "x_axis_label_buff": SMALL_BUFF,
        #"x_axis_label_orientation":  # TO BE IMPLEMENTED
        
        "y_min": -1,
        "y_max": 10,
        "y_axis_height": 6,
        "y_tick_frequency": 1,
        "y_bottom_tick": None,  # Change if different from y_min
        "y_labeled_nums": None,
        "y_elongated_nums": None,
        "y_axis_label": "$y$",
        "y_axis_label_position": UR,
        "y_axis_label_buff": SMALL_BUFF,
        #"y_axis_label_orientation":  # TO BE IMPLEMENTED
        
        "default_dot_radius": 0.04,
        "default_dot_opacity": 1.0,
        "default_dot_stroke_width": 0,
        
        "default_bar_rwidth": 1.0,
        "default_bar_opacity": 1.0,
        "default_bar_stroke_width": 0,
        "default_bar_align": LEFT,  # For mid align use ORIGIN
        
        "axes_color": GREY,
        "exclude_zero_label": True,
        "default_graph_colors": [BLUE, GREEN, YELLOW],
        "default_derivative_color": GREEN,
        "default_input_color": YELLOW,
        "default_riemann_start_color": BLUE,
        "default_riemann_end_color": GREEN,
        "area_opacity": 0.8,
        "num_rects": 50,
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        #digest_config(self, kwargs)
        #if self.max_value is None:
        #    self.max_value = max(values)

        #self.add_axes()
        #self.add_bars(values)
        self.graph_origin = (0,0,0)
        self.setup()
        self.setup_axes()
        self.center()
    
    def setup(self):
        self.default_graph_colors_cycle = it.cycle(self.default_graph_colors)
        #self.left_T_label = VGroup()
        #self.left_v_line = VGroup()
        #self.right_T_label = VGroup()
        #self.right_v_line = VGroup()

    def setup_axes(self, animate=False):
        # X axis ---------------------
        x_num_range = float(self.x_max - self.x_min)
        self.space_unit_to_x = self.x_axis_width / x_num_range
        if self.x_labeled_nums is None:
            self.x_labeled_nums = []
        if self.x_elongated_nums is None:
            self.x_elongated_nums = []
        if self.x_leftmost_tick is None:
            self.x_leftmost_tick = self.x_min
        x_axis = NumberLine(
            x_min=self.x_min,
            x_max=self.x_max,
            unit_size=self.space_unit_to_x,
            tick_frequency=self.x_tick_frequency,
            leftmost_tick=self.x_leftmost_tick,
            numbers_with_elongated_ticks=self.x_elongated_nums,
            color=self.axes_color
        )
        if len(self.x_labeled_nums) > 0:
            if self.exclude_zero_label:
                self.x_labeled_nums = [x for x in self.x_labeled_nums
                                       if x != 0]
            x_axis.add_numbers(*self.x_labeled_nums)
        if self.x_axis_label:
            x_label = TextMobject(self.x_axis_label)
            x_label.next_to(
                x_axis.get_corner(self.x_axis_label_position),
                self.x_axis_label_position,
                buff=self.x_axis_label_buff,
            )
            x_axis.add(x_label)
            self.x_axis_label_mob = x_label
        # Y axis ---------------------
        y_num_range = float(self.y_max - self.y_min)
        self.space_unit_to_y = self.y_axis_height / y_num_range
        if self.y_labeled_nums is None:
            self.y_labeled_nums = []
        if self.y_elongated_nums is None:
            self.y_elongated_nums = []
        if self.y_bottom_tick is None:
            self.y_bottom_tick = self.y_min
        y_axis = NumberLine(
            x_min=self.y_min,
            x_max=self.y_max,
            unit_size=self.space_unit_to_y,
            tick_frequency=self.y_tick_frequency,
            leftmost_tick=self.y_bottom_tick,
            numbers_with_elongated_ticks=self.y_elongated_nums,
            color=self.axes_color,
            label_direction=LEFT,
        )
        y_axis.shift(self.graph_origin - y_axis.number_to_point(0))
        y_axis.rotate(np.pi / 2, about_point=y_axis.number_to_point(0))
        if len(self.y_labeled_nums) > 0:
            if self.exclude_zero_label:
                self.y_labeled_nums = [y for y in self.y_labeled_nums
                                       if y != 0]
            y_axis.add_numbers(*self.y_labeled_nums)
        if self.y_axis_label:
            y_label = TextMobject(self.y_axis_label)
            y_label.next_to(
                y_axis.get_corner(self.y_axis_label_position),
                self.y_axis_label_position,
                buff=self.y_axis_label_buff,
            )
            y_axis.add(y_label)
            self.y_axis_label_mob = y_label
        # Add axes
        self.add(x_axis, y_axis)
        self.x_axis, self.y_axis = self.axes = VGroup(x_axis, y_axis)
        self.default_graph_colors = it.cycle(self.default_graph_colors)

    def add_dots(self, x=None, y=None, data=None, color=None, radius=None,
                 fill_opacity=None, stroke_width=None, **kwargs):
        if data is not None:
            x = data[0]
            y = data[1]
        elif x is None:
            x = []
            for i in range(1, len(y)+1):
                x.append(i)
        if color is None:
            color = next(self.default_graph_colors_cycle)
        if radius is None:
            radius = self.default_dot_radius
        if fill_opacity is None:
            fill_opacity = self.default_dot_opacity
        if stroke_width is None:
            stroke_width = self.default_dot_stroke_width

        dot_sequence = VGroup()
        for i in range(len(y)):
            point = self.coords_to_point(x[i], y[i])
            dot_sequence.add(Dot(
                                color=color,
                                radius=radius,
                                fill_opacity=fill_opacity,
                                stroke_width=stroke_width,
                                **kwargs,
                                ).move_to(point))
        if hasattr(self, "dot_sequences") is False:
            self.dot_sequences = VGroup()
        self.dot_sequences.add(dot_sequence)
        self.add(self.dot_sequences)
        return dot

    def add_bars(self, x=None, y=None, data=None, color=None, rwidth=None,
                 fill_opacity=None, stroke_width=None, align=None, **kwargs):
        if data is not None:
            x = data[0]
            y = data[1]
        elif x is None:
            x = []
            for i in range(1,len(y)+1):
                x.append(i)
        if color is None:
            color = next(self.default_graph_colors_cycle)
        if rwidth is None:
            rwidth = self.default_bar_rwidth
        if fill_opacity is None:
            fill_opacity = self.default_bar_opacity
        if stroke_width is None:
            stroke_width = self.default_bar_stroke_width
        if align is None:
            align = self.default_bar_align

        bar_sequence = VGroup()
        for i in range(len(y)):
            base = self.coords_to_point(x[i], 0)
            point_x, point_y, point_z = self.coords_to_point(x[i], y[i])
            point_x0, point_y0, point_z0 = self.coords_to_point(0, 0)
            if i < len(y)-1:
                point_x1, point_y1, point_z1 = self.coords_to_point(x[i+1],
                                                                    y[i+1])
            else:
                point_x1, point_y1, point_z1 = self.coords_to_point(x[i-1],
                                                                    y[i-1])
            height = point_y - point_y0
            gap = abs(point_x1 - point_x)
            width = rwidth*gap
            bar = Rectangle(
                    height=height,
                    width=width,
                    color=color,
                    fill_opacity=fill_opacity,
                    stroke_width=stroke_width,
                    **kwargs,
                    ).next_to(base, UP+align, buff=0)
            bar.shift((1-rwidth)*align*gap/2)
            bar_sequence.add(bar)
        if hasattr(self, "bar_sequences") is False:
            self.bar_sequences = VGroup()
        self.bar_sequences.add(bar_sequence)
        self.add(self.bar_sequences)
        return bar

    def add_curve(self, func, color=None, x_min=None, x_max=None,
                  parameters=None, **kwargs):
        if color is None:
            color = next(self.default_graph_colors_cycle)
        if x_min is None:
            x_min = self.x_min
        if x_max is None:
            x_max = self.x_max

        def parameterized_function(alpha, **parameters):
            x = interpolate(x_min, x_max, alpha)
            y = func(x, **parameters)
            if not np.isfinite(y):
                y = self.y_max
            return self.coords_to_point(x, y)

        curve = ParametricFunction(parameterized_function,
                                   parameters=parameters,
                                   color=color,
                                   **kwargs)
        curve.underlying_function = func
        if hasattr(self, "curves") is False:
            self.curves = VGroup()
        self.curves.add(curve)
        self.add(self.curves)
        return curve

    def copy(self):
        return self.deepcopy()

    def coords_to_point(self, x, y):
        assert(hasattr(self, "x_axis") and hasattr(self, "y_axis"))
        result = self.x_axis.number_to_point(x)[0] * RIGHT
        result += self.y_axis.number_to_point(y)[1] * UP
        return result

    def point_to_coords(self, point):
        return (self.x_axis.point_to_number(point),
                self.y_axis.point_to_number(point))
