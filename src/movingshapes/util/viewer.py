# viewer.py
# A simple viewer for performances from the Heider-Simmel Interactive Theater and Triangle Charades applications
# 2024 Andrew S. Gordon 
# Uses the graphics.py library (GPL) written by John Zelle for use with the book "Python Programming: An Introduction to Computer Science" (Franklin, Beedle & Associates). 

import graphics
import pandas as pd
import time
import math
import sys

def rotate(x,y,theta):
    x2 = x * math.cos(math.radians(theta)) - y * math.sin(math.radians(theta))
    y2 = x * math.sin(math.radians(theta)) + y * math.cos(math.radians(theta))
    return (x2,y2)

class Viewer:

    # class variables

    line_width = 9.05 # default for 400. If 500, then should be 9.05 * 500/400
    stage = None
    bt = True
    lt = True
    c = True
    door = True
    win = False
    dataframe = False
 
    # class methods
    
    def circle_xy(self, x, y):
        self.c = graphics.Circle(graphics.Point(0,0), 170)
        self.c.setFill("black")
        self.c.move(x,y)
        self.c.draw(self.win)

    def bt_xyr(self, x, y, r):
        self.bt = graphics.Polygon(graphics.Point(*rotate(-250,143.34,r)),
                          graphics.Point(*rotate(0,-288.68,r)),
                          graphics.Point(*rotate(250,144.34,r)))
        self.bt.move(x,y)
        self.bt.setFill("black")
        self.bt.draw(self.win)

    def lt_xyr(self, x, y, r):
        self.lt = graphics.Polygon(graphics.Point(*rotate(-190,115,r)),
                 graphics.Point(*rotate(0,-214,r)),
                 graphics.Point(*rotate(190,115,r)))
        self.lt.move(x,y)
        self.lt.setFill("black")
        self.lt.draw(self.win)

    def door_r(self, r):
        self.door = graphics.Line(graphics.Point(*rotate(0,-800, r)), graphics.Point(0,0))
        self.door.setWidth(self.line_width)
        self.door.move(1573,1430)
        self.door.draw(self.win)

    def stage(self, window_width = 640):
        self.win = graphics.GraphWin("Viewer", window_width, 0.75 * window_width, autoflush=False)
        self.win.setCoords(0,3000,4000,0)
        self.line_width = 9.05 * window_width / 400
        if self.dataframe['ltx'].sum() == 0.0: # 1 character charades
            self.stage = '1c_charades'
            self.draw_1c_charades_stage()
        elif self.dataframe['cx'].sum() == 0.0: # 2 character charades
            self.stage = '2c_charades'
            self.draw_2c_charades_stage()
        else:
            self.stage = 'hsit'
            self.draw_hsit_stage()

    def draw_hsit_stage(self):
        self.circle_xy(3540,700)
        self.bt_xyr(3540,2100,0)
        self.lt_xyr(3540,1400,0)
        self.door_r(10)
        w1 = graphics.Line(graphics.Point(400,2435), graphics.Point(1600,2435))
        w1.setWidth(self.line_width)
        w1.draw(self.win)
        w2 = graphics.Line(graphics.Point(424,545), graphics.Point(424,2480))
        w2.setWidth(self.line_width)
        w2.draw(self.win)
        w3 = graphics.Line(graphics.Point(1573,2480), graphics.Point(1573,1410))
        w3.setWidth(self.line_width)
        w3.draw(self.win)
        w4 = graphics.Line(graphics.Point(400,590), graphics.Point(1618,590))
        w4.setWidth(self.line_width)
        w4.draw(self.win)

    def draw_1c_charades_stage(self):
        self.bt_xyr(2000, 1500, 0)

    def draw_2c_charades_stage(self):
        self.bt_xyr(2350, 1500, 0)
        self.lt_xyr(1650, 1500, 0)

    def draw_row(self, row):
        if self.stage == 'hsit':
            self.draw_hsit_row(row)
        elif self.stage == '1c_charades':
            self.draw_1c_charades_row(row)
        elif self.stage == '2c_charades':
            self.draw_2c_charades_row(row)
        else:
            print(self.stage)

    def draw_hsit_row(self, row):
        self.bt.undraw()
        self.lt.undraw()
        self.c.undraw()
        self.door.undraw()
        self.bt_xyr(row[1], row[2], row[3])
        self.lt_xyr(row[4], row[5], row[6])
        self.circle_xy(row[7], row[8])
        self.door_r(row[10])
        graphics.update()

    def draw_1c_charades_row(self, row):
        self.bt.undraw()
        self.bt_xyr(row[1], row[2], row[3])
        graphics.update()

    def draw_2c_charades_row(self, row):
        self.bt.undraw()
        self.lt.undraw()
        self.bt_xyr(row[1], row[2], row[3])
        self.lt_xyr(row[4], row[5], row[6])
        graphics.update()
   
    def get_row(self, time):
        rownum = 0
        last_time = self.dataframe['ms'].iloc[-1]
        if time >= last_time:
            return self.dataframe.iloc[-1, :].to_list()
        while self.dataframe.loc[rownum, 'ms'] < time:
            rownum += 1
        return self.dataframe.iloc[rownum, :].to_list()

    def play(self):
        last_time = self.dataframe['ms'].iloc[-1]
        start_time = time.time() * 1000
        elapsed_time = 0
        while elapsed_time <= last_time:
            self.draw_row(self.get_row(elapsed_time))
            elapsed_time = (time.time() * 1000) - start_time
        return(self)

    def play_segment(self, start, end):
        start_time = time.time() * 1000
        elapsed_time = 0
        while elapsed_time + start <= end:
            self.draw_row(self.get_row(elapsed_time + start))
            elapsed_time = (time.time() * 1000) - start_time
        return(self)

    def seek(self, time):
        self.draw_row(self.get_row(time))
    
    def from_file(self, fn):
        self.dataframe = pd.read_csv(fn, names=['ms','btx','bty','btr','ltx','lty','ltr','cx','cy','cr','dr'], delimiter=' ')
        self.stage()
        self.seek(0)
        return(self)
    
    def interpolate(self, ms=10):
        stop_ms = self.dataframe['ms'].max() + ms
        df = self.dataframe.set_index('ms')
        df = df.reindex(pd.RangeIndex(start = 0, stop = stop_ms))
        df = df.interpolate(limit_direction='both', limit_area='inside', limit=ms)
        df = df.fillna(method='pad')
        df = df.fillna(method='bfill')
        df = df[::ms]
        df = df.reset_index(names=['ms'], level=0)
        self.dataframe = df
        return(self)

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("usage: > python viewer.py filename")
        exit()
    
    v = Viewer().from_file(filename) # as recorded
    # v = Viewer().from_file(filename).interpolate(33) # smoother
    
    v.win.getMouse()
    v.play()
    v.win.getMouse()
    v.win.close()

if __name__ == '__main__':
    main()

