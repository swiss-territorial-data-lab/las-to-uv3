#!/usr/bin/env python3
#  las-to-uv3
#
#     Huriel Reichel - huriel.ruan@gmail.com
#     Nils Hamel - nils.hamel@bluewin.ch
#     Copyright (c) 2020 STDL, Swiss Territorial Data Lab
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from laspy.file import File
from struct import *

import argparse
import math
import sys
import os
from matplotlib import cm

def scaled_x_dimension(inFile):
        x_dimension = inFile.X
        scale = inFile.header.scale[0]
        offset = inFile.header.offset[0]
        return(x_dimension*scale + offset)

def scaled_y_dimension(inFile):
        y_dimension = inFile.Y
        scale = inFile.header.scale[1]
        offset = inFile.header.offset[1]
        return(y_dimension*scale + offset)
    
# Borrowed from Federal Office of Topography swisstopo, Wabern, CH and Aaron Schmocker 
# https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py
# Convert CH y/x to WGS lat
def CHtoWGSlat(self, y, x):
        # Axiliary values (% Bern)
        y_aux = (y - 600000) / 1000000
        x_aux = (x - 200000) / 1000000
        lat = (16.9023892 + (3.238272 * x_aux)) + \
                - (0.270978 * pow(y_aux, 2)) + \
                - (0.002528 * pow(x_aux, 2)) + \
                - (0.0447 * pow(y_aux, 2) * x_aux) + \
                - (0.0140 * pow(x_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lat = (lat * 100) / 36
        return lat

# Convert CH y/x to WGS long
def CHtoWGSlng(self, y, x):
        # Axiliary values (% Bern)
        y_aux = (y - 600000) / 1000000
        x_aux = (x - 200000) / 1000000
        lng = (2.6779094 + (4.728982 * y_aux) + \
                + (0.791484 * y_aux * x_aux) + \
                + (0.1306 * y_aux * pow(x_aux, 2))) + \
                - (0.0436 * pow(y_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lng = (lng * 100) / 36
        return lng

def las_to_uv3(input, output, classification, intensity, rgb):

    inFile = File(input, mode='r')
    
    if (rgb == False and classification == False and intensity == False):
        
        # create output stream #
        with open( output, mode='wb' ) as uv3:
            
            for i in range(len(inFile.points)):
                
                #print( inFile.points[i] )
                
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                # An argument shall be passed to this coordinates system conversion step
                X = CHtoWGSlng(True, Y, X)
                Y = CHtoWGSlat(True, Y, X)
                
                X = X * (math.pi / 180) 
                X = X.astype(float)
                
                Y = Y * (math.pi / 180) 
                Y = Y.astype(float)
                
                Z = inFile.points[i][0][2]
                Z = Z / 1000
                Z = Z.astype(float)
                
                #print( 'debug c', X, Y, Z );
                
                inferno = cm.get_cmap('inferno', 4800)
                pal = inferno(Z)
                R = pal[0] * 255
                G = pal[1] * 255
                B = pal[3] * 255
                R = R.astype(int)
                G = G.astype(int)
                B = B.astype(int)
                
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B)
                uv3.write( pm_buffer )
                
            print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
    
    elif (rgb == True and classification == False and intensity == False):
        
        #### colours to rgb
        with open( output, mode='wb' ) as uv3:
            
            for i in range(len(inFile.points)):
                
                #print( inFile.points[i] )
                
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                # An argument shall be passed to this coordinates system conversion step
                X = CHtoWGSlng(True, Y, X)
                Y = CHtoWGSlat(True, Y, X)
                
                X = X * (math.pi / 180) 
                X = X.astype(float)
                
                Y = Y * (math.pi / 180) 
                Y = Y.astype(float)
                
                Z = inFile.points[i][0][2]
                Z = Z / 1000
                Z = Z.astype(float)
                
                R = inFile.points[i][0][10]
                G = inFile.points[i][0][11]
                B = inFile.points[i][0][12]
                
            # pack and write 
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B )
                uv3.write( pm_buffer )
            print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
         
    elif (rgb == False and classification == True and intensity == False ):
        
        with open( output, mode='wb' ) as uv3:
        
            for point in inFile.points:
                
                X = inFile.X
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                Y = inFile.Y
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                # An argument shall be passed to this coordinates system conversion step
                X = CHtoWGSlng(True, Y, X)
                Y = CHtoWGSlat(True, Y, X)
                
                X = X * (math.pi / 180) 
                X = X.astype(float)
                
                Y = Y * (math.pi / 180) 
                Y = Y.astype(float)
                
                Z = inFile.points[i][0][2]
                Z = Z / 1000
                Z = Z.astype(float)   
                
                # undefined / reserved / user defined
                if point[0][7] <= 1 and point[0][7] == 8 and point[0][7] == 12 and point[0][7] >= 19:
                    R = 255
                    G = 255
                    B = 255
            
                # ground
                if point[0][7] == 2:
                    R = 209
                    G = 224
                    B = 224
                    
                # low vegetation
                if point[0][7] == 3:
                    R = 70
                    G = 225
                    B = 100
                
                # medium vegetation
                if point[0][7] == 4:
                    R = 70
                    G = 199
                    B = 100
                
                # high vegetation
                if point[0][7] == 5:
                    R = 70
                    G = 152
                    B = 100
                
                # building
                if point[0][7] == 6:
                    R = 241
                    G = 182
                    B = 88
                       
                # low point
                if point[0][7] == 7:
                    R = 0
                    G = 0
                    B = 156
                
                # reserved *
                if point[0][7] == 8:
                    R = 255
                    G = 255
                    B = 255
                
                # water
                if point[0][7] == 9:
                    R = 0
                    G = 201
                    B = 255
                
                # rail
                if point[0][7] == 10:
                    R = 211
                    G = 213
                    B = 215
                
                # road
                if point[0][7] == 11:
                    R = 229
                    G = 0
                    B = 0
                                                     
                # wire 
                if point[0][7] >= 13 and point[0][7] < 15:
                    R = 32
                    G = 0
                    B = 124    
                
                # transmission tower
                if point[0][7] == 15:
                    R = 248
                    G = 240
                    B = 92
                
                # wire 
                if point[0][7] == 16:
                    R = 32
                    G = 0
                    B = 124
                
                # bridge deck 
                if point[0][7] == 17:
                    R = 234
                    G = 231
                    B = 165
                
                #print( 'debug c', X, Y, Z );
                
                                                                     
            # pack and write 
            pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B )
            uv3.write( pm_buffer )
        print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
         
    else :
       
        # create output stream #
        with open( output, mode='wb' ) as uv3:
          
            for i in range(len(inFile.points)):
                
                #print( inFile.points[i] )
                
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                # An argument shall be passed to this coordinates system conversion step
                X = CHtoWGSlng(True, Y, X)
                Y = CHtoWGSlat(True, Y, X)
                
                X = X * (math.pi / 180) 
                X = X.astype(float)
                
                Y = Y * (math.pi / 180) 
                Y = Y.astype(float)
                
                Z = inFile.points[i][0][2]
                Z = Z / 1000
                Z = Z.astype(float)
                
               # print( 'debug c', X, Y, Z );
                
                I = inFile.points[i][0][3]
                inferno = cm.get_cmap('inferno', 4800)
                pal = inferno(I)
                R = pal[0] * 255
                G = pal[1] * 255
                B = pal[3] * 255
                R = R.astype(int)
                G = G.astype(int)
                B = B.astype(int)
                
                #pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B)
                #uv3.write( pm_buffer )
                
            print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
    
pm_argparse = argparse.ArgumentParser()

# argument and parameter directive #
pm_argparse.add_argument( '-i', '--input', type=str  , help='geotiff path'    )
pm_argparse.add_argument( '-o', '--output' , type=str  , help='uv3 output path' )
pm_argparse.add_argument( '-r', '--rgb', type=bool, default = False, help='whether rgb values are recorded in the las file. Default to False' )
pm_argparse.add_argument( '-c', '--classification', type=bool, default = False, help='whether colours should refer to point classification. Default to False' )
pm_argparse.add_argument( '-t', '--intensity', type=bool, default=False, help='whether colours should refer to intensity. Default to False' )

# read argument and parameters #
pm_args = pm_argparse.parse_args()      
        
        # create output stream #

# display message #
print( 'Processing file : ' + os.path.basename( pm_args.input ) + '...' )

# process file #
las_to_uv3( pm_args.input, pm_args.output, pm_args.rgb, pm_args.classification, pm_args.intensity )

# exit script #
sys.exit( 'Done' )
