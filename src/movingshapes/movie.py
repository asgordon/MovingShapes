# src/movingshapes/movie.py
# Utility for exporting performances as movies or images
# August 2025

from PIL import Image, ImageDraw
import math, os, tempfile, subprocess

class Movie:

    def __init__(self, performance, size = (640,480), coordinates = (4000,3000), fps = 24):
        self.size = size
        self.coordinates = coordinates
        self.stage = performance.stage
        self.data = performance.data
        self.fps = fps
        self.linewidth = round(9.05 * self.size[0] / 400)

    def row_at_time(self, ms):
        res = self.data[0].copy()
        for row in self.data:
            if row[0] > ms: break
            res = row.copy()
            res[0] = ms
        return res
        
    def frame_data(self):
        res = []
        fps_ms = 1000.0 / self.fps
        data_end = self.data[-1][0]
        seek = 0.0
        while seek < data_end:
            res.append(self.row_at_time(seek))
            seek  += fps_ms
        res.append(self.row_at_time(seek)) # don't forget the last video frame
        return res
    
    def image_at_time(self, ms): # returns a PIL.Image
        row = self.row_at_time(ms)
        img = Image.new('RGB', self.size, color='white')
        if self.stage == "box-bt-lt-c":
            self.draw_big_triangle(img, row[1], row[2], row[3])
            self.draw_little_triangle(img, row[4], row[5], row[6])
            self.draw_circle(img, row[7], row[8])
            self.draw_door(img, row[10])
            self.draw_box(img)
        elif self.stage == "bt-lt":
            self.draw_big_triangle(img, row[1], row[2], row[3])
            self.draw_little_triangle(img, row[4], row[5], row[6])
        elif self.stage == "bt":
            self.draw_big_triangle(img, row[1], row[2], row[3])
        return img
    
    def rotate(self, x,y,theta):
        x2 = x * math.cos(math.radians(theta)) - y * math.sin(math.radians(theta))
        y2 = x * math.sin(math.radians(theta)) + y * math.cos(math.radians(theta))
        return (x2,y2)

    def scale_distance(self, coordinate_distance):
        return coordinate_distance * self.size[0] / self.coordinates[0]
    
    def translate(self, point, translation):
        return (point[0] + translation[0], point[1] + translation[1])
    
    def scale_point(self, coordinate_point):
        return (self.scale_distance(coordinate_point[0]), self.scale_distance(coordinate_point[1]))

    def draw_big_triangle(self, img, x, y, r):
        translation = (self.scale_distance(x), self.scale_distance(y))
        draw = ImageDraw.Draw(img)
        draw.polygon((self.translate(self.scale_point(self.rotate(-250,143.34,r)), translation),
                        self.translate(self.scale_point(self.rotate(0,-288.68,r)), translation),
                        self.translate(self.scale_point(self.rotate(250,144.34,r)), translation)),
                        fill = (0,0,0))

    def draw_little_triangle(self, img, x, y, r):
        translation = (self.scale_distance(x), self.scale_distance(y))
        draw = ImageDraw.Draw(img)
        draw.polygon((self.translate(self.scale_point(self.rotate(-190,115,r)), translation),
                          self.translate(self.scale_point(self.rotate(0,-214,r)), translation),
                          self.translate(self.scale_point(self.rotate(190,115,r)), translation)),
                          fill = (0,0,0))

    def draw_circle(self, img, x, y):
        draw = ImageDraw.Draw(img)
        radius = self.scale_distance(170)
        center_x = self.scale_distance(x)
        center_y = self.scale_distance(y)
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=(0, 0, 0))

    def draw_door(self, img, r):
        draw = ImageDraw.Draw(img)
        translation = (self.scale_distance(1573), self.scale_distance(1430))
        draw.line((self.translate(self.scale_point(self.rotate(0,-800, r)), translation),
                        self.translate((0,0), translation)),
                        fill = (0,0,0),
                        width=self.linewidth)

    def draw_box(self, img):
        draw = ImageDraw.Draw(img)
        draw.line((self.scale_point((400,2435)),
                        self.scale_point((1600,2435))),
                        fill = (0,0,0),
                        width=self.linewidth)
        draw.line((self.scale_point((424,545)),
                        self.scale_point((424,2480))),
                        fill = (0,0,0),
                        width=self.linewidth)
        draw.line((self.scale_point((1573,2480)),
                        self.scale_point((1573,1410))),
                        fill = (0,0,0),
                        width=self.linewidth)
        draw.line((self.scale_point((400,590)),
                        self.scale_point((1618,590))),
                        fill = (0,0,0),
                        width=self.linewidth)

    def image_as_stage(self): # returns PIL.Image
        img = Image.new('RGB', self.size, color='white')
        if self.stage == "box-bt-lt-c":
            self.draw_circle(img, 3540, 700)
            self.draw_big_triangle(img, 3540,2100,0)
            self.draw_little_triangle(img, 3540,1400,0)
            self.draw_door(img, 10)
            self.draw_box(img)
        elif self.stage == "bt":
            self.draw_big_triangle(img, 2000, 1500, 0)
        elif self.stage == "bt-lt":
            self.draw_big_triangle(img, 2350, 1500, 0)
            self.draw_little_triangle(img, 1650, 1500, 0)
        return img

    def save_frames(self, dir):
        fps_ms = 1000.0 / self.fps
        data_end = self.data[-1][0]
        seek = 0.0
        framenum = 0
        while seek < data_end:
            path = os.path.join(dir, "frame" + "{:04}".format(framenum) + ".png")
            self.image_at_time(seek).save(path)
            seek  += fps_ms
            framenum += 1

    def save(self, path):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.save_frames(temp_dir)
            cmd = [
                "ffmpeg",
                "-framerate", str(self.fps),
                "-i", os.path.join(temp_dir, "frame%04d.png"), # wildcard pattern
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                path
            ]
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                raise("ffmpeg failed:", e)
            except FileNotFoundError:
                raise("ffmpeg not found (required). See here for installation instructions: https://ffmpeg.org/ ", e)

