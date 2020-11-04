#!/usr/bin/env python3
#  las-to-uv3
#
#     Huriel Reichel - huriel.ruan@gmail.com
#     Nils Hamel - nils.hamel@bluewin.ch
#     Alessandro Cerioni - alessandro.cerioni@etat.ge.ch
#     Copyright (c) 2020 Republic and Canton of Geneva
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
from struct import pack

import argparse
import math
import sys
import os
import time
from matplotlib import cm

# Defining scaling functions
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

# Borrowed and Adapted from Aaron Schmocker [aaron@duckpond.ch]
# Source: http://www.swisstopo.admin.ch/internet/swisstopo/en/home/topics/survey/sys/refsys/projections.html (see PDFs under "Documentation")
# guthub script: https://github.com/hurielreichel/Swisstopo-WGS84-LV03/blob/master/scripts/py/wgs84_ch1903.py
class GPSConverter(object):
    '''
    GPS Converter class which is able to perform convertions between the 
    CH1903 and WGS84 system.
    '''
    # Convert CH y/x/h to WGS height
    def CHtoWGSheight(self, y, x, h):
        # Axiliary values (% Bern)
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
        h = (h + 49.55) - (12.60 * y_aux) - (22.64 * x_aux)
        return h

    # Convert CH y/x to WGS lat
    def CHtoWGSlat(self, y, x):
        # Axiliary values (% Bern)
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
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
        y_aux = (y - 2600000) / 1000000
        x_aux = (x - 1200000) / 1000000
        lng = (2.6779094 + (4.728982 * y_aux) + \
                + (0.791484 * y_aux * x_aux) + \
                + (0.1306 * y_aux * pow(x_aux, 2))) + \
                - (0.0436 * pow(y_aux, 3))
        # Unit 10000" to 1" and convert seconds to degrees (dec)
        lng = (lng * 100) / 36
        return lng

    def LV03toWGS84(self, east, north, height):
        '''
        Convert LV03 to WGS84 Return a array of double that contain lat, long,
        and height
        '''
        d = []
        d.append(self.CHtoWGSlat(east, north))
        d.append(self.CHtoWGSlng(east, north))
        d.append(self.CHtoWGSheight(east, north, height))
        return d
    
# Main function
def las_to_uv3(input, output, classification, intensity, rgb):
    
    # reading LiDAR data
    inFile = File(input, mode='r')

    # defining values for the colour pallete, for both height and intensity
    h = (inFile.z + 49.55) - (12.60 * ((inFile.y - 2600000) / 1000000)) - (22.64 * ((inFile.x - 1200000) / 1000000))
    min_h = min(h)
    max_h = max(h)

    min_t = min(inFile.intensity)
    max_t = max(inFile.intensity) / 100
    
    # defining colour palette
    inferno = cm.get_cmap('inferno', 100) 
    
    # Colours based on height
    if (rgb == 0 and classification == 0 and intensity == 0):
        
        print("colouring by elevation")
        
        # create output stream #
        with open( output, mode='wb' ) as uv3:
            
            for i in range(len(inFile.points)):
                
                # scaling coordinates
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                Z = inFile.points[i][0][2]
                Z = Z / 100
                
                # An argument shall be passed to this coordinate system conversion step  
                converter = GPSConverter()
                lv03 = [X, Y, Z]
                wgs84 = converter.LV03toWGS84(lv03[0], lv03[1], lv03[2])
                
                X = wgs84[1]
                Y = wgs84[0]
                Z = wgs84[2]
                
                # converting from degrees to radians
                X = X * (math.pi / 180) 
                Y = Y * (math.pi / 180) 
                
                # colouring based on elevation
                feat_scal = ( Z - min_h) / (max_h - min_h)  
                pal = inferno(feat_scal)
                                
                R = pal[0] * 255
                G = pal[1] * 255
                B = pal[2] * 255
                R = R.astype(int)
                G = G.astype(int)
                B = B.astype(int)
               
                # pack and write 
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B)
                uv3.write( pm_buffer )      
            #print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
    
    # Colours based on given RGB values
    elif (rgb == 1 and classification == 0 and intensity == 0):
        
        print("colouring by given RGB")
        
        #### colours to rgb
        with open( output, mode='wb' ) as uv3:
            
            for i in range(len(inFile.points)):
                
                # scaling coordinates
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                Z = inFile.points[i][0][2]
                Z = Z / 100
                
                # An argument shall be passed to this coordinate system conversion step  
                converter = GPSConverter()
                lv03 = [X, Y, Z]
                wgs84 = converter.LV03toWGS84(lv03[0], lv03[1], lv03[2])
                
                X = wgs84[1]
                Y = wgs84[0]
                Z = wgs84[2]
               
                # converting from degrees to radians
                X = X * (math.pi / 180) 
                Y = Y * (math.pi / 180) 
                
                # colouring based on given RGB values
                R = inFile.points[i][0][10]
                G = inFile.points[i][0][11]
                B = inFile.points[i][0][12]
                
                # pack and write 
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B )
                uv3.write( pm_buffer )
            #print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
         
    # Colours based on raw classification
    elif (rgb == 0 and classification == 1 and intensity == 0 ):
        
        print("colouring by classification")
        
        with open( output, mode='wb' ) as uv3:
        
            for i in range(len(inFile.points)):
                
                # scaling coordinates
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                Z = inFile.points[i][0][2]
                Z = Z / 100
                
                # An argument shall be passed to this coordinate system conversion step  
                converter = GPSConverter()
                lv03 = [X, Y, Z]
                wgs84 = converter.LV03toWGS84(lv03[0], lv03[1], lv03[2])
                
                X = wgs84[1]
                Y = wgs84[0]
                Z = wgs84[2]
               
                # converting from degrees to radians
                X = X * (math.pi / 180) 
                Y = Y * (math.pi / 180) 
                
                # colouring based on raw classification
                # this can be changed to address your specific values
                
                # undefined / reserved / user defined
                if inFile.points[i][0][5] <= 1 or inFile.points[i][0][5] == 8 or inFile.points[i][0][5] == 12 or inFile.points[i][0][5] >= 19:
                    R = 255
                    G = 255
                    B = 255
            
                # ground
                if inFile.points[i][0][5] == 2:
                    R = 209
                    G = 224
                    B = 224
                    
                # low vegetation
                if inFile.points[i][0][5] == 3:
                    R = 70
                    G = 225
                    B = 100
                
                # medium vegetation
                if inFile.points[i][0][5] == 4:
                        R = 70
                        G = 199
                        B = 100
                
                # high vegetation
                if inFile.points[i][0][5] == 5:
                    R = 70
                    G = 152
                    B = 100
                
                # building
                if inFile.points[i][0][5] == 6:
                    R = 241
                    G = 182
                    B = 88
                       
                # low point
                if inFile.points[i][0][5] == 7:
                    R = 0
                    G = 0
                    B = 156
                
                # reserved *
                if inFile.points[i][0][5] == 8:
                    R = 255
                    G = 255
                    B = 255
                        
                # water
                if inFile.points[i][0][5] == 9:
                    R = 0
                    G = 201
                    B = 255
                        
                # rail
                if inFile.points[i][0][5] == 10:
                    R = 211
                    G = 213
                    B = 215
                
                # road
                if inFile.points[i][0][5] == 11:
                    R = 229
                    G = 0
                    B = 0
                                                         
                # wire 
                if inFile.points[i][0][5] >= 13 and inFile.points[i][0][5] < 15:
                    R = 32
                    G = 0
                    B = 124    
                
                # transmission tower
                if inFile.points[i][0][5] == 15:
                    R = 248
                    G = 240
                    B = 92
                
                # wire 
                if inFile.points[i][0][5] == 16:
                    R = 32
                    G = 0
                    B = 124
                
                # bridge deck 
                if inFile.points[i][0][5] == 17:
                    R = 234
                    G = 231
                    B = 165
                
                # pack and write 
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B )
                uv3.write( pm_buffer )
            #print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
    
    # Colours based on intensity
    else :
       
        print("colouring by intensity")
        # create output stream #
        with open( output, mode='wb' ) as uv3:
          
            for i in range(len(inFile.points)):
                
                # scaling coordinates
                X = inFile.points[i][0][0] 
                X = X * inFile.header.scale[0] + inFile.header.offset[0]
                
                Y = inFile.points[i][0][1]
                Y = Y * inFile.header.scale[1] + inFile.header.offset[1]
                
                Z = inFile.points[i][0][2]
                Z = Z / 100
                
                # An argument shall be passed to this coordinate system conversion step  
                converter = GPSConverter()
                lv03 = [X, Y, Z]
                wgs84 = converter.LV03toWGS84(lv03[0], lv03[1], lv03[2])
                
                X = wgs84[1]
                Y = wgs84[0]
                Z = wgs84[2]
               
                # converting from degreed to radians
                X = X * (math.pi / 180) 
                Y = Y * (math.pi / 180) 
                
                # colouring by intensity
                I = inFile.points[i][0][3]
                feat_scal = ( I - min_t) / ( max_t - min_t )
                pal = inferno(feat_scal)
                
                R = pal[0] * 255
                G = pal[1] * 255
                B = pal[2] * 255
                R = R.astype(int)
                G = G.astype(int)
                B = B.astype(int)
                
                pm_buffer = pack( '<dddBBBB', X, Y, Z, 1, R, G, B)
                uv3.write( pm_buffer )
                
            #print( X, Y, Z, 1, R, G, B ) # in chase you want to print results as the former Octave code
    
pm_argparse = argparse.ArgumentParser()

# argument and parameter directive #
pm_argparse.add_argument( '-i', '--input', type=str  , help='geotiff path'    )
pm_argparse.add_argument( '-o', '--output' , type=str  , help='uv3 output path' )
pm_argparse.add_argument( '-r', '--rgb', type=int, default = 0, help='whether rgb values are recorded in the las file. Default to False' )
pm_argparse.add_argument( '-c', '--classification', type=int, default = 0, help='whether colours should refer to point classification. Default to False' )
pm_argparse.add_argument( '-t', '--intensity', type=int, default=0, help='whether colours should refer to intensity. Default to False' )

# read argument and parameters #
pm_args = pm_argparse.parse_args()      

# display message #
print( 'Processing file : ' + os.path.basename( pm_args.input ) + '...' )

tic = time.time()

# process file #
las_to_uv3( pm_args.input, pm_args.output, pm_args.classification, pm_args.intensity, pm_args.rgb )

toc = time.time()

# exit script #
sys.exit(f'Done. Elapsed time = {(toc-tic):.2f} seconds.' )