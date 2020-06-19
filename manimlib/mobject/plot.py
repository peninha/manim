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


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            (hasattr(arg, "__getitem__") or hasattr(arg, "__iter__")))


class Plot(VGroup):
    CONFIG = {
        "x_min": 0,
        "x_max": 10,
        "x_axis_width": 9,
        "x_tick_frequency": 1,
        "x_leftmost_tick": None,  # Change if different from x_min
        "x_labeled_nums": None,
        "x_elongated_nums": None,
        "x_axis_label": "$x$",
        "x_axis_label_position": UR,
        "x_axis_label_buff": SMALL_BUFF,
        # "x_axis_label_orientation":  # TO BE IMPLEMENTED

        "y_min": 0,
        "y_max": 10,
        "y_axis_height": 6,
        "y_tick_frequency": 1,
        "y_bottom_tick": None,  # Change if different from y_min
        "y_labeled_nums": None,
        "y_elongated_nums": None,
        "y_axis_label": "$y$",
        "y_axis_label_position": UR,
        "y_axis_label_buff": SMALL_BUFF,
        # "y_axis_label_orientation":  # TO BE IMPLEMENTED

        "default_dot_radius": 0.04,
        "default_dot_opacity": 1.0,
        "default_dot_stroke_width": 0,

        "default_bar_opacity": 1.0,
        "default_bar_stroke_width": 0,

        "default_hist_bins": 10,
        "default_hist_density": False,
        "default_hist_rwidth": 1,

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
        self.setup()
        self.setup_axes()
        self.center()

    def setup(self):
        self.default_graph_colors_cycle = it.cycle(self.default_graph_colors)
        # self.left_T_label = VGroup()
        # self.left_v_line = VGroup()
        # self.right_T_label = VGroup()
        # self.right_v_line = VGroup()

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
        y_axis.shift(-1 * y_axis.number_to_point(0))
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

    def scatter(self, x, y, size=None, color=None, fill_opacity=None,
                stroke_width=None, **kwargs):
        if color is None:
            color = it.cycle([next(self.default_graph_colors_cycle)])
        else:
            if is_sequence(color):
                color = it.cycle(color)
            else:
                color = it.cycle([color])
        if size is None:
            size = self.default_dot_radius
        if fill_opacity is None:
            fill_opacity = self.default_dot_opacity
        if stroke_width is None:
            stroke_width = self.default_dot_stroke_width

        scatter_sequence = VGroup()
        for i in range(len(y)):
            point = self.coords_to_point(x[i], y[i])
            dot = Dot(
                    color=next(color),
                    radius=size,
                    fill_opacity=fill_opacity,
                    stroke_width=stroke_width,
                    **kwargs,
                    ).move_to(point)
            scatter_sequence.add(dot)
        if hasattr(self, "scatter_sequences") is False:
            self.scatter_sequences = VGroup()
        self.scatter_sequences.add(scatter_sequence)
        self.add(self.scatter_sequences)
        return scatter_sequence

    def bar(self, x, height, width=0.8, align='center', color=None,
            fill_opacity=None, stroke_width=None, **kwargs):
        if len(x) != len(height):
            raise ValueError("'x' and 'height' should be equal sized")
        if align == 'center':
            align = ORIGIN
        elif align == 'edge' or align == 'right':
            align = RIGHT
        elif align == 'left':
            align = LEFT
        if color is None:
            color = it.cycle([next(self.default_graph_colors_cycle)])
        else:
            if is_sequence(color):
                color = it.cycle(color)
            else:
                color = it.cycle([color])
        if fill_opacity is None:
            fill_opacity = self.default_bar_opacity
        if stroke_width is None:
            stroke_width = self.default_bar_stroke_width

        bar_sequence = VGroup()
        p_x0, p_y0, p_z0 = self.coords_to_point(0, 0)
        for i in range(len(x)):
            if is_sequence(width):
                bar_width = width[i]
            else:
                bar_width = width
            p_x1, p_y1, p_z1 = self.coords_to_point(x[i], height[i])
            p_x2, p_y2, p_z2 = self.coords_to_point(bar_width, 0)
            bar_height = p_y1 - p_y0
            bar_width = p_x2 - p_x0
            bar_center = (p_x1, p_y0, p_z1)
            bar = Rectangle(
                    height=bar_height,
                    width=bar_width,
                    color=next(color),
                    fill_opacity=fill_opacity,
                    stroke_width=stroke_width,
                    **kwargs,
                    ).next_to(bar_center, UP+align, buff=0)
            bar_sequence.add(bar)
        if hasattr(self, "bar_sequences") is False:
            self.bar_sequences = VGroup()
        self.bar_sequences.add(bar_sequence)
        self.add(self.bar_sequences)
        return bar_sequence

    def hist(self, x, bins=None, bin_range=None, density=None, weights=None,
             cumulative=False, histtype='bar', align='mid',
             orientation='vertical', rwidth=None, log=False, color=None,
             label=None, stacked=False, normed=None,
             fill_opacity=None, stroke_width=None, **kwargs):
        if bins is None:
            bins = self.default_hist_bins
        if bin_range is None:
            bin_range = (min(x), max(x))
        if density is None:
            density = self.default_hist_density
        if align == 'mid':
            align = ORIGIN
        elif align == 'right':
            align = RIGHT
        elif align == 'left':
            align = LEFT
        if rwidth is None:
            rwidth = self.default_hist_rwidth
        if color is None:
            color = it.cycle([next(self.default_graph_colors_cycle)])
        else:
            if is_sequence(color):
                color = it.cycle(color)
            else:
                color = it.cycle([color])
        if fill_opacity is None:
            fill_opacity = self.default_bar_opacity
        if stroke_width is None:
            stroke_width = self.default_bar_stroke_width

        data, bin_edges = np.histogram(
            x,
            bins=bins,
            range=bin_range,
            weights=weights,
            density=density,
            )

        histogram = VGroup()
        for i in range(len(bin_edges)-1):
            x0, y0, z0 = self.coords_to_point(bin_edges[i], 0)
            x1, y1, z1 = self.coords_to_point(bin_edges[i+1], data[i])
            bin_width = x1 - x0
            bin_center = (x0, y0, z0) + bin_width/2 * (RIGHT + align)
            bar_height = y1 - y0
            bar_width = rwidth * bin_width
            bar = Rectangle(
                height=bar_height,
                width=bar_width,
                color=next(color),
                fill_opacity=fill_opacity,
                stroke_width=stroke_width,
                **kwargs,
                ).next_to(bin_center, UP, buff=0)
            histogram.add(bar)
        if hasattr(self, "hist_sequences") is False:
            self.hist_sequences = VGroup()
        self.hist_sequences.add(histogram)
        self.add(self.hist_sequences)
        return data, bin_edges, histogram


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

    #def copy(self):
    #    return self.deepcopy()

    def coords_to_point(self, x, y):
        assert(hasattr(self, "x_axis") and hasattr(self, "y_axis"))
        result = self.x_axis.number_to_point(x)[0] * RIGHT
        result += self.y_axis.number_to_point(y)[1] * UP
        return result

    def point_to_coords(self, point):
        return (self.x_axis.point_to_number(point),
                self.y_axis.point_to_number(point))
