# movie.py - Generate movies of Moving Shapes data
# Andrew S. Gordon / September 2024

from PIL import Image, ImageDraw
import moviepy.editor as mp
import numpy as np
import math

class HSFrame:

    # local variablers 

    img = None
    draw = None

    def __init__(self, size = (640,480), coordinates = (4000,3000), stage = "box-bt-lt-c", data = None):
        self.size = size
        self.coordinates = coordinates
        self.stage = stage
        self.data = data
        self.linewidth = round(9.05 * self.size[0] / 400)

    def rotate(self, x,y,theta):
        x2 = x * math.cos(math.radians(theta)) - y * math.sin(math.radians(theta))
        y2 = x * math.sin(math.radians(theta)) + y * math.cos(math.radians(theta))
        return (x2,y2)
        
    def as_stage(self):
        self.img = Image.new('RGB', self.size, color='white')
        self.draw = ImageDraw.Draw(self.img)
        if self.stage == "box-bt-lt-c":
            self.draw_circle(3540, 700)
            self.draw_big_triangle(3540,2100,0)
            self.draw_little_triangle(3540,1400,0)
            self.draw_door(10)
            self.draw_box()
        elif self.stage == "bt":
            self.draw_big_triangle(2000, 1500, 0)
        elif self.stage == "bt-lt":
            self.draw_big_triangle(2350, 1500, 0)
            self.draw_little_triangle(1650, 1500, 0)
        return self.img
    
    def scale_distance(self, coordinate_distance):
        return coordinate_distance * self.size[0] / self.coordinates[0]
    
    def scale_point(self, coordinate_point):
        return (self.scale_distance(coordinate_point[0]), self.scale_distance(coordinate_point[1]))
    
    def translate(self, point, translation):
        return (point[0] + translation[0], point[1] + translation[1])

    def draw_circle(self, x, y):
        radius = self.scale_distance(170)
        center_x = self.scale_distance(x)
        center_y = self.scale_distance(y)
        self.draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=(0, 0, 0))

    def draw_big_triangle(self, x, y, r):
        translation = (self.scale_distance(x), self.scale_distance(y))
        self.draw.polygon((self.translate(self.scale_point(self.rotate(-250,143.34,r)), translation),
                          self.translate(self.scale_point(self.rotate(0,-288.68,r)), translation),
                          self.translate(self.scale_point(self.rotate(250,144.34,r)), translation)),
                          fill = (0,0,0))
        
    def draw_little_triangle(self, x, y, r):
        translation = (self.scale_distance(x), self.scale_distance(y))
        self.draw.polygon((self.translate(self.scale_point(self.rotate(-190,115,r)), translation),
                          self.translate(self.scale_point(self.rotate(0,-214,r)), translation),
                          self.translate(self.scale_point(self.rotate(190,115,r)), translation)),
                          fill = (0,0,0))
        

    def draw_door(self, r):
        translation = (self.scale_distance(1573), self.scale_distance(1430))
        width = 9.05 * self.size[0] / 400
        self.draw.line((self.translate(self.scale_point(self.rotate(0,-800, r)), translation),
                        self.translate((0,0), translation)),
                        fill = (0,0,0),
                        width=self.linewidth)

    def draw_box(self):
        self.draw.line((self.scale_point((400,2435)),
                        self.scale_point((1600,2435))),
                        fill = (0,0,0),
                        width=self.linewidth)
        self.draw.line((self.scale_point((424,545)),
                        self.scale_point((424,2480))),
                        fill = (0,0,0),
                        width=self.linewidth)
        self.draw.line((self.scale_point((1573,2480)),
                        self.scale_point((1573,1410))),
                        fill = (0,0,0),
                        width=self.linewidth)
        self.draw.line((self.scale_point((400,590)),
                        self.scale_point((1618,590))),
                        fill = (0,0,0),
                        width=self.linewidth)


    def at_time(self, ms):
        res = self.data[0]
        for row in self.data:
            if row[0] > ms: break
            res = row
        self.img = Image.new('RGB', self.size, color='white')
        self.draw = ImageDraw.Draw(self.img)
        if self.stage == "box-bt-lt-c":
            self.draw_big_triangle(row[1], row[2], row[3])
            self.draw_little_triangle(row[4], row[5], row[6])
            self.draw_circle(row[7], row[8])
            self.draw_door(row[10])
            self.draw_box()
        elif self.stage == "bt-lt":
            self.draw_big_triangle(row[1], row[2], row[3])
            self.draw_little_triangle(row[4], row[5], row[6])
        elif self.stage == "bt":
            self.draw_big_triangle(row[1], row[2], row[3])
        return self.img
            


class HSMovie:

    def __init__(self, performance, size = (640,480), coordinates = (4000,3000), fps = 24):
        self.size = size
        self.coordinates = coordinates
        self.stage = performance.stage
        self.data = performance.data
        self.fps = fps

    def save_frames(self, dir):
        fps_ms = 1000.0 / self.fps
        data_end = self.data[-1][0]
        seek = 0.0
        framenum = 0
        while seek < data_end:
            frame = HSFrame(data = self.data).at_time(seek)
            fn = dir + "/frame" + "{:04}".format(framenum) + ".png"
            frame.save(fn)
            seek  += fps_ms
            framenum += 1

    # ffmpeg -framerate 24 -pattern_type glob -i "frames/*.png" -c:v libx264 -pix_fmt yuv420p out.mp4
        
    def save(self, output_path):
        frames = []
        fps_ms = 1000.0 / self.fps
        data_end = self.data[-1][0]
        seek = 0.0
        framenum = 0
        while seek < data_end:
            frame = HSFrame(data = self.data, stage = self.stage).at_time(seek)
            frames.append(mp.ImageClip(np.array(frame), duration = fps_ms / 1000.0))
            seek  += fps_ms
            framenum += 1
        # don't forget the last frame, where seek >= data_end
        frame = HSFrame(data = self.data, stage = self.stage).at_time(seek)
        frames.append(mp.ImageClip(np.array(frame), duration = fps_ms / 1000.0))
        # now concat those together
        clip = mp.concatenate_videoclips(frames)
        clip.write_videofile(output_path, fps = self.fps)

    def row_at_time(self, ms):
        res = self.data[0]
        for row in self.data:
            if row[0] > ms: break
            res = row
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