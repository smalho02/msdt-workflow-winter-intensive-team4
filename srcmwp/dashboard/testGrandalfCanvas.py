# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 24, 2012
@author: blubin
'''

from wax import Frame;
from wax import Application;
from grandalfCanvas import GrandalfCanvas;
from grandalfCanvas import NodeProperties;
from grandalf.graphs import Vertex;
from grandalf.graphs import Edge;
from grandalf.graphs import Graph;

class MainFrame(Frame):
    def Body(self):
        self.SetSize((800,600));
        canvas = GrandalfCanvas(self)
        G, p = self.get_graph();
        canvas.set_graph(G, p);

    def get_graph(self):
        V = [Vertex(data) for data in range(10)]
        X = [(0,1),(0,2),(1,3),(2,3),(4,0),(1,4),(4,5),(5,6),(3,6),(3,7),(6,8), (7,8),(8,9),(5,9)]
        E = [Edge(V[v],V[w]) for (v,w) in X]
        g = Graph(V,E)
        p = [NodeProperties() for v in V];
        return g, p;

if __name__ == '__main__':
    app = Application(MainFrame)
    app.MainLoop()
