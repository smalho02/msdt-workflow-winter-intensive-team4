# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 24, 2012
@author: blubin
'''

import wx;
from wx.lib.floatcanvas.NavCanvas import NavCanvas;
from grandalf.layouts import SugiyamaLayout;
from grandalf.routing import route_with_lines;

class NodeProperties(object):
    def __init__(self, name = "Unknown", color = (150,150,150)):
        self.name = name;
        self.color = color;

class NodeViewer(object):
    def __init__(self, w, h):
        self.w=w;
        self.h=h;

class EdgeViewer(object):
    def setpath(self,pts):
        self.pts = pts;

class GrandalfCanvas(NavCanvas):
    '''
    A Float Canvas that knows how to display a Gandalf fraph
    '''

    def __init__(self, parent, uid = wx.NewId(), size = wx.DefaultSize, **kwargs):
        NavCanvas.__init__(self, parent, uid, size, **kwargs);

    def set_graph(self, G, props):
        self.Canvas.ClearAll(); 
        for v in G.V(): 
            v.view = NodeViewer(25, 1);
        for e in G.E():
            e.view = EdgeViewer();
        # TODO: offset each component so they don't overlap.
        for c in G.C: 
            self.add_component(G, props, c);
           
    def add_component(self, G, props, c):
        sug = SugiyamaLayout(c);
        sug.xspace = 3;
        sug.yspace = 3;
        sug.dw = 1;
        sug.dh = 1;
        sug.route_edge = route_with_lines;
        sug.init_all()
        sug.draw()
    
        for v in c.V():
            ref = v.data;
            prop = props[ref];
            name = prop.name;
            color = prop.color;
            pos = v.view.xy;
            w = v.view.w;
            h = v.view.h;
            self.Canvas.AddRectangle((pos[0]-(w/2.0), pos[1]-h), (w,h), FillColor=color, LineWidth=2);
            #self.Canvas.AddScaledText(name,(pos[0], pos[1]-(h/2.0)), .8*h, Position="cc");
            self.Canvas.AddScaledTextBox(name,(pos[0], pos[1]-(h/2.0)), .8*h, Position="cc", LineColor=None);
        for e in c.E():
            h=1 # should set from node, but just hard code for now.
            pts = e.view.pts;
            pts = list(pts);
            pts.reverse();
            pts[0] = (pts[0][0], pts[0][1]-h);
            #Draw regular line up to the last point:
            if len(pts)>2:
                self.Canvas.AddLine(pts[0:-1], LineWidth=3);
            self.Canvas.AddArrowLine(pts[-2:], LineWidth=3, ArrowHeadSize=15);
        wx.CallAfter(self.Canvas.ZoomToBB);
        