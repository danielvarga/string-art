import sys
import numpy as np
import scipy
import scipy.sparse
import scipy.sparse.linalg
from scipy.misc import imread, imresize, imsave
import math
from collections import defaultdict

from bresenham import *


def image(filename, size):
    img = imresize(imread(filename, flatten=True), (size, size))
    return img


def main():
    filename, output_filename = sys.argv[1:]

    n = 180
    radius = 120

    # square image with same center as the circle, sides are 95% of circle diameter.
    img = image(filename, int(radius * 2 * 0.75))

    print "building sparse adjecency matrix"
    hooks = np.array([[math.cos(np.pi*2*i/n), math.sin(np.pi*2*i/n)] for i in range(n)])
    hooks = (radius * hooks).astype(int)
    edge_codes = []
    row_ind = []
    col_ind = []
    for i, ni in enumerate(hooks):
        for j, nj in enumerate(hooks[i+1:], start=i+1):
            edge_codes.append((i, j))
            pixels = bresenham(ni, nj).path
            edge = []
            for pixel in pixels:
                pixel_code = (pixel[1]+radius)*(radius*2+1) + (pixel[0]+radius)
                edge.append(pixel_code)
            row_ind += edge
            col_ind += [len(edge_codes)-1] * len(edge)
    # creating the edge-pixel adjecency matrix:
    # rows are indexed with pixel codes, columns are indexed with edge codes.
    sparse = scipy.sparse.csr_matrix(([1.0]*len(row_ind), (row_ind, col_ind)), shape=((2*radius+1)*(2*radius+1), len(edge_codes)))

    # representing the input image as a sparse column vector of pixels:
    assert img.shape[0] == img.shape[1]
    img_size = img.shape[0]
    row_ind = []
    col_ind = []
    data = []
    for y, line in enumerate(img):
        for x, pixel_value in enumerate(line):
            global_x = x - img_size//2
            global_y = y - img_size//2
            pixel_code = (global_y+radius)*(radius*2+1) + (global_x+radius)
            data.append(pixel_value)
            row_ind.append(pixel_code)
            col_ind.append(0)
    sparse_b = scipy.sparse.csr_matrix((data, (row_ind, col_ind)), shape=(sparse.shape[0], 1))

    # finding the solution, a weighting of edges:
    print "solving linear system"
    # note the .todense(). for some reason the sparse version did not work.
    result = scipy.sparse.linalg.lsqr(sparse, np.array(sparse_b.todense()).flatten())
    print "done"
    x = result[0]
    # negative values are clipped, they are physically unrealistic.
    x = np.clip(x, 0, 1e6)

    # quantizing:
    quantization_level = None # 50 is already quite good. None means no quantization.

    # clip values larger than clip_factor times maximum.
    # (The long tail does not add too much to percieved quality.)
    clip_factor = 0.3
    if quantization_level is not None:
        max_edge_weight_orig = np.max(x)
        x_quantized = (x / np.max(x) * quantization_level).round()
        x_quantized = np.clip(x_quantized, 0, int(np.max(x_quantized) * clip_factor))
        # scale it back:
        x = x_quantized / quantization_level * max_edge_weight_orig

    # reconstruction:
    b_approx = sparse.dot(x)
    b_image = b_approx.reshape((2*radius+1, 2*radius+1))
    b_image = np.clip(b_image, 0, 255)
    imsave(output_filename, b_image)

    if quantization_level is not None:
        arc_count = 0
        total_distance = 0.0
        hist = defaultdict(int)
        for edge_code, multiplicity in enumerate(x_quantized):
            multiplicity = int(multiplicity)
            hist[multiplicity] += 1
            arc_count += multiplicity
            hook_index1, hook_index2 = edge_codes[edge_code]
            hook1, hook2 = hooks[hook_index1], hooks[hook_index2]
            distance = np.linalg.norm(hook1.astype(float) - hook2.astype(float)) / radius
            total_distance += distance
        for multiplicity in range(max(hist.keys())+1):
            print multiplicity, hist[multiplicity]
        print "total arc count", arc_count
        print "total distance (with unit radius)", total_distance

main()
