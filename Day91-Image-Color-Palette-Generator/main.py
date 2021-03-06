# Day91-Professional Portfolio Project 11 : Image Color Palette Generator
# K-Means reference link : https://curiousily.com/posts/color-palette-extraction-with-k-means-clustering/

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from math import sqrt
from PIL import Image
import random

dir_path = 'static/uploaded_images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = dir_path
app.config['SECRET_KEY'] = 'afkjhakfakjsdjka'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

img_path = None

class Point:

    def __init__(self, coordinates):
        self.coordinates = coordinates


class Cluster:

    def __init__(self, center, points):
        self.center = center
        self.points = points


class KMeans:

    def __init__(self, n_clusters, min_diff=1):
        self.n_clusters = n_clusters
        self.min_diff = min_diff

    def calculate_center(self, points):
        n_dim = len(points[0].coordinates)
        vals = [0.0 for i in range(n_dim)]
        for p in points:
            for i in range(n_dim):
                vals[i] += p.coordinates[i]

        coords = [(v / len(points)) for v in vals]

        return Point(coords)

    def assign_points(self, clusters, points):
        plists = [[] for i in range(self.n_clusters)]

        for p in points:
            smallest_distance = float('inf')

            for i in range(self.n_clusters):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i

            plists[idx].append(p)

        return plists

    def fit(self, points):
        clusters = [Cluster(center=p, points=[p]) for p in random.sample(points, self.n_clusters)]

        while True:
            plists = self.assign_points(clusters, points)

            diff = 0

            for i in range(self.n_clusters):
                if not plists[i]:
                    continue

                old = clusters[i]
                center = self.calculate_center(plists[i])
                new = Cluster(center, plists[i])
                clusters[i] = new
                diff = max(diff, euclidean(old.center, new.center))

            if diff < self.min_diff:
                break

        return clusters


def euclidean(p, q):
    n_dim = len(p.coordinates)
    return sqrt(sum([(p.coordinates[i] - q.coordinates[i]) ** 2 for i in range(n_dim)]))


def get_points(image_path):
    img = Image.open(image_path)
    img.thumbnail((200, 400))
    img = img.convert('RGB')
    w, h = img.size

    points = []
    for count, color in img.getcolors(w * h):
        for _ in range(count):
            points.append(Point(color))

    return points

def rgb_to_hex(rgb):
    # return '#%s' % ''.join(('%02x' % p for p in rgb))
    return ''.join(('%02x' % p for p in rgb))


def hex_to_rgb(hex):
    rgb = []
    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)


def get_colors(filename, n_colors=10):
    points = get_points(filename)
    clusters = KMeans(n_clusters=n_colors).fit(points)
    clusters.sort(key=lambda c: len(c.points), reverse=True)
    rgbs = [map(int, c.center.coordinates) for c in clusters]

    return list(map(hex_to_rgb, (map(rgb_to_hex, rgbs))))


@app.route("/", methods=['GET', 'POST'])
def home():
    global img_path

    if request.method == 'POST':
        file = request.files['img_file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        img_path = dir_path + '/' + filename

        return redirect(url_for('home'))

    elif request.method == 'GET' and img_path:
        top_ten_colors = get_colors(img_path, n_colors=10)

        print("top_ten_colors", top_ten_colors)

        return render_template('index.html', colors=top_ten_colors, imgpath=img_path)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)