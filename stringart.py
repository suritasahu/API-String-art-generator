import math
import copy
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance


class StringArtGenerator:
    def __init__(self):
        self.iterations = 1000
        self.shape = 'circle'
        self.image = None
        self.data = None
        self.residual = None
        self.seed = 0
        self.nails = 100
        self.weight = 10
        self.nodes = []
        self.paths = []

    def set_seed(self, seed):
        self.seed = seed

    def set_weight(self, weight):
        self.weight = weight

    def set_shape(self, shape):
        self.shape = shape

    def set_nails(self, nails):
        self.nails = nails
        if self.shape == 'circle':
            self.set_nodes_circle()
        elif self.shape == 'rectangle':
            self.set_nodes_rectangle()

    def set_iterations(self, iterations):
        self.iterations = iterations

    def set_nodes_rectangle(self):
        perimeter = self.get_perimeter()
        spacing = perimeter / self.nails
        width, height = np.shape(self.data)

        pnails = [t * spacing for t in range(self.nails)]

        xarr = []
        yarr = []
        for p in pnails:
            if (p < width):  # top edge
                x = p
                y = 0
            elif (p < width + height):  # right edge
                x = width
                y = p - width
            elif (p < 2 * width + height):  # bottom edge
                x = width - (p - width - height)
                y = height
            else:  # left edge
                x = 0
                y = height - (p - 2 * width - height)
            xarr.append(x)
            yarr.append(y)

        self.nodes = list(zip(xarr, yarr))

    def get_perimeter(self):
        return 2.0 * np.sum(np.shape(self.data))

    def set_nodes_circle(self):
        spacing = (2 * math.pi) / self.nails

        steps = range(self.nails)

        radius = self.get_radius()

        x = [radius + radius * math.cos(t * spacing) for t in steps]
        y = [radius + radius * math.sin(t * spacing) for t in steps]

        self.nodes = list(zip(x, y))

    def get_radius(self):
        return 0.5 * np.amax(np.shape(self.data))

    def load_image(self, path):
        img = Image.open(path)
        self.image = img
        np_img = np.array(self.image)
        self.data = np.flipud(np_img).transpose()

    def preprocess(self):
        self.image = ImageOps.grayscale(self.image)
        self.image = ImageOps.invert(self.image)
        self.image = self.image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        self.image = ImageEnhance.Contrast(self.image).enhance(1)
        np_img = np.array(self.image)
        self.data = np.flipud(np_img).transpose()

    def generate(self):
        self.calculate_paths()
        delta = 0.0
        pattern = []
        nail = self.seed
        datacopy = copy.deepcopy(self.data)
        for i in range(self.iterations):
            darkest_nail, darkest_path = self.choose_darkest_path(nail)
            pattern.append(self.nodes[darkest_nail])
            self.data = self.data - self.weight * darkest_path
            self.data[self.data < 0.0] = 0.0

            if (np.sum(self.data) <= 0.0):
                print("Stopping iterations. No more data or residual unchanged.")
                break

            delta = np.sum(self.data)
            nail = darkest_nail

        self.residual = copy.deepcopy(self.data)
        self.data = datacopy

        return pattern

    def choose_darkest_path(self, nail):
        max_darkness = -1.0
        for index, rowcol in enumerate(self.paths[nail]):
            rows = [i[0] for i in rowcol]
            cols = [i[1] for i in rowcol]
            darkness = float(np.sum(self.data[rows, cols]))

            if darkness > max_darkness:
                darkest_path = np.zeros(np.shape(self.data))
                darkest_path[rows, cols] = 1.0
                darkest_nail = index
                max_darkness = darkness

        return darkest_nail, darkest_path

    def calculate_paths(self):
        for nail, anode in enumerate(self.nodes):
            self.paths.append([])
            for node in self.nodes:
                path = self.bresenham_path(anode, node)
                self.paths[nail].append(path)

    def bresenham_path(self, start, end):
        x1, y1 = start
        x2, y2 = end

        x1 = max(0, min(round(x1), self.data.shape[0] - 1))
        y1 = max(0, min(round(y1), self.data.shape[1] - 1))
        x2 = max(0, min(round(x2), self.data.shape[0] - 1))
        y2 = max(0, min(round(y2), self.data.shape[1] - 1))

        dx = x2 - x1
        dy = y2 - y1

        path = []

        if (start == end):
            return path

        is_steep = abs(dy) > abs(dx)

        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx = x2 - x1
        dy = y2 - y1

        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        y = y1
        for x in range(x1, x2 + 1):
            if is_steep:
                path.append([y, x])
            else:
                path.append([x, y])
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

        return path
