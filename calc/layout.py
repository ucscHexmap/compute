#!/usr/bin/env python2.7
"""
layout.py: Given a matrix of similarities, produce a hexagram visualization.

This script takes in the filename of a tab-separated value file containing a
sparse similarity matrix (with string labels) and several matrices of
layer/score data. It produces an HTML file (and several support files) that
provide an interactive visualization of the items clustered on a hexagonal grid.

This script depends on the DrL graph layout package, binaries for which must be
present in your PATH.

Re-uses sample code and documentation from 
<http://users.soe.ucsc.edu/~karplus/bme205/f12/Scaffold.html>

Notes about peculiarities in code:
    1.) --include_singletons option: the name suggests you are including nodes
        that would otherwise not be there, but from the code it is clear this is
        not the case. --include_singletons simply draws a self connecting edge
        on all the nodes already on the map before running through DRL. It is
        unclear what affect this should have on a spring embedded layout
        clustering algorithm. Its action can be viewed in the
        drl_similarity_functions() code.
        Update: Testing with the mcrchropra test data suggests this
        argument does nothing.
    2.) --truncate_edges option: This is defaulted to 6, and gets fed into the
        DRL clustering algorithm. The name suggests that even if you provided
        20 neighbors, downstream the DRL clustering algorithm would trim it
        down to six.
"""

DEV = False # True if in development mode, False if not

import argparse, os, itertools, math, subprocess, shutil, tempfile, glob
import collections, traceback, datetime, pprint, string
import time
from types import *
import os.path
import tsv, csv, json
from utils import sigDigs
from statsNoLayout import statsNoLayout
from topNeighbors import topNeighbors
from topNeighbors import topNeighbors_from_sparse
from compute_sparse_matrix import read_tabular
from compute_sparse_matrix import compute_similarities
from compute_sparse_matrix import extract_similarities
import compute_sparse_matrix
import StringIO
from utils import getAttributes
import leesL
import sklearn.metrics
import sklearn.metrics.pairwise as sklp
import numpy as np
from process_categoricals import create_colormaps_file
import utils
import formatCheck
import sys

validReflectionMapTypes = \
    ['geneMatrix']

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # WebAPI / CWL / CLI: Primary parameters:
    parser.add_argument("--layoutInputFile", action='append',
        help="file containing the layout data as TSV")
    parser.add_argument("--distanceMetric", type=str, default="spearman",
        help="metric corresponding to the layout input data of the same " +
        "index, one of: " + compute_sparse_matrix.valid_metrics())
        # TODO Which layout formats use this? All of them to draw edges in
        # the node density view?
    parser.add_argument("--layoutName", type=str, action="append", dest="names",
        default=[],
        help="human-readable unique label for the layout of the same index")
    parser.add_argument("--colorAttributeFile", type=str, dest="scores",
        action="append",
        help="file containing the attributes to color the map, as TSV")
    parser.add_argument("--colormaps", type=str,
        default='',
        help="colormap for categorical attributes as TSV")
    parser.add_argument("--firstAttribute", type=str, dest="first_attribute",
        default="",
        help="attribute to color the map upon first display")
    parser.add_argument("--outputDirectory", "-d", type=str, dest="directory",
        help="directory in which to create view output files")
    parser.add_argument("--authGroup", type=str, dest="role",
        default=None,
        help="authorization group that may view this map")
    parser.add_argument("--zeroReplace", action='store_true',
        default=False,
        help="Replaces NA values with 0")
    parser.add_argument("--nodeIdSearchUrl", type=str,
                        default="https://www.google.com/search?q=",
        help="The search string URL to be prepended to the nodeId")
    parser.add_argument("--doingRows", action='store_true',
        default=False,
        help="If a feature matrix is given, this flag transposes it in order"
             " to perform row-wise similarity calculation")

    # WebAPI / CWL / CLI: Lesser used parameters:
    parser.add_argument("--reflectionMapType", type=str, default=None,
        help="generate another map with 90-degree rotated clustering data " +
        "so that clustering features are used as the nodes in the layout. " +
        "Color attributes are provided and determined by the map type. One " +
        "of: " + str(validReflectionMapTypes))
    parser.add_argument("--attributeTags", type=str,
        default=None,
        help="tags for filtering attributes for display, as TSV")
    parser.add_argument("--noLayoutIndependentStats", dest="associations",
        action="store_false", default=True,
        help="don't calculate layout-independent stats")
    parser.add_argument("--noLayoutAwareStats", dest="mutualinfo",
        action="store_false", default=True,
        help="don't calculate layout-aware stats")
    parser.add_argument("--neighborCount", type=int, default=6,
        dest="truncation_edges",
        help="edges per node for DrL and the directed graph")
        
    # CWL / CLI:
    parser.add_argument("--outputZip", type=str, default="", dest="output_zip",
        help="compress the output files into a zip file")
    parser.add_argument("--outputTar", type=str, default="", dest="output_tar",
        help="compress the output files into this tar file")

    # CLI only:
    parser.add_argument("--drlPath", "-r", type=str, dest="drlpath",
        help="DrL binaries")

    # Deprecated parameters:
    parser.add_argument("--coordinates", type=str, action='append',
        help="deprecated, use layoutInputFile instead & format will be auto-detected")
    parser.add_argument("--directed_graph", dest="directedGraph",
        action="store_true", default=True,
        help="deprecated with constant value of true")
        # old help="generate the data to draw the directed graph in the node" +
        #    "density view")
    parser.add_argument("--directory", type=str, default=".",
        help="deprecated, use 'outputDirectory' instead")
    parser.add_argument("--drlpath", type=str, dest="drlpath",
        help="deprecated, use 'drlPath' instead")
    parser.add_argument("--feature_space", type=str, action='append',
        help="deprecated, use layoutInputFile & format will be auto-detected")
    parser.add_argument("--first_attribute", type=str, default="",
        help="deprecated, use 'firstAttribute' instead")
    parser.add_argument("--include-singletons", dest="singletons",
        action="store_true", default=False,
        help="deprecated with a constant value of true")
    parser.add_argument("--layoutInputFormat", type=str,
        help="deprecated, format is auto-detected")
    parser.add_argument("--names", type=str, action="append", default=[],
        help="deprecated, use 'layoutName' instead")
    parser.add_argument("--no_layout_independent_stats", dest="associations",
        action="store_false", default=True,
        help="deprecated, use 'noLayoutIndependentStats' instead")
    parser.add_argument("--no_layout_aware_stats", dest="mutualinfo",
        action="store_false", default=True,
        help="deprecated, use 'noLayoutAwareStats' instead")
    parser.add_argument("--metric", type=str, dest="distanceMetric",
        default="spearman",
        help="deprecated, use 'distanceMetric' instead")
    parser.add_argument("--output_tar", type=str, default="",
        help="deprecated, use 'outputTar' instead")
    parser.add_argument("--output_zip", type=str, default="",
        help="deprecated, use 'output_zip' instead")
    parser.add_argument("--role", type=str, default=None,
        help="deprecated, use 'authGroup' instead")
    parser.add_argument("--scores", type=str, action="append",
        help="deprecated, use 'colorAttributeFile' instead")
    parser.add_argument("--self-connected-edges", dest="singletons",
        action="store_true", default=False,
        help="deprecated with a constant value of true")
        # old help="add self-edges to input of DRL algorithm")
    parser.add_argument("--similarity", type=str, action='append',
        help="deprecated, use layoutInputFile & format will be auto-detected")
    parser.add_argument("--similarity_full", type=str, action='append',
        help="deprecated, use layoutInputFile & format will be auto-detected")
    parser.add_argument("--truncation_edges", type=int, default=6,
        help="deprecated, use 'neighborCount' instead")
    parser.add_argument("--window_size", type=int, default=20,
        help="deprecated with no substitute")
        # old help="clustering window count is this value squared")

    parser.add_argument("--layoutMethod", type=str, default="DrL",
        help="DrL, tete")
    #parser.add_argument("--preprocess_method", type=str, default="",
    #    help="Preprocessing methods for feature data when tSNE, MDS, PCA, ICA, isomap, or spectralembedding methods are used; valid options are: standardize, normalize")
    #parser.add_argument("--tsne_pca_dimensions", type=str, default="11",
    #    help="Number of PCA dimensions to reduce data to prior to performing t-SNE")

    return parser.parse_args(args)

def sparsePandasToString(sparseDataFrame):
    '''
    converts a sparse matrix, to edgefile formatted output string
    @param sparseDataFrame: pandas dataframe
    @return: the proper string representation of a sparse matrix
    '''
    #text buffer
    s_buf = StringIO.StringIO()
    #dump pandas data frame into buffer
    sparseDataFrame.to_csv(s_buf,sep='\t',header=False,index=None)
    #dump the buffer into a string
    bigstr = s_buf.getvalue()
    #final manipulation to match output necessary for rest of the script
    bigstr = '\n' + bigstr[:-1]

    return bigstr

def getCategoricalsFromColorMapFile(filename,debug=False):
    '''
    :param filename: the name of the colormaps file
    :return: a list of attributes thought to be categorical by the colormaps processor
    '''
    if debug:
        print 'getting categoricals from ' + filename
    colormaps_reader = tsv.TsvReader(open(filename, 'r'))
    categoricals = []
    for row in colormaps_reader:
        categoricals.append(row[0])
    colormaps_reader.close()

    return categoricals

def checkForBinaryCategorical(catAtts,datatypes):
    '''
    looks for attributes that are named categorical, because they have a colormap
     but only have two categories, and therefor should be treated as binaries
    :param catAtts: the attribute dataframe for categical attributes
    :param datatypes:
    :return: a refined datatypes,
    '''
    for attr in catAtts.columns:
        #print attr
        #print len(catAtts[attr].dropna().unique())
        if len(catAtts[attr].dropna().unique()) == 2:
            #print 'found bin'
            datatypes['bin'].append(attr)
            datatypes['cat'].remove(attr)

    return datatypes

def getDataTypes(attributeDF,colormapFile,debug=False):
    '''
    logic for getting datatype from attribute files,
         also checks to make sure an attribute in the colormap has an attribute in the scores/attribute matrix
    :param attributeDF: The pandas dataframe that holds all the attributes for a map
    :param colormapFile: The name/path to the colormap file, used to determine possible categoricals
    :return: a dictionary {'bin' -> ['binary_attrname',...,],
                            'cont' -> ['continuous_attrname',...,],
                           'cat' -> ['categorical_attrname',...,]
                          }

    '''

    categoricals =  getCategoricalsFromColorMapFile(colormapFile)
    binaries = []
    continuouses = []
    if debug:
        print 'categoricals read: ' + str(len(categoricals))
        print categoricals

    prunedCats = []
    #remove any attriibutes that made there way into the colormap but aren't in the metadata
    for attrName in categoricals:
        if debug:
            print attrName
        if attrName in attributeDF.columns.tolist() and \
            attrName not in prunedCats:
            prunedCats.append(attrName)
        else:
            if debug:
                print 'removed'

    categoricals= prunedCats

    #figure out the datatype
    for attrName in attributeDF.columns:
        # if the name was in the colormap, and in the attribute matrix then, for now, it's a categorical
        if attrName in categoricals:
            continue
        #otherwise if it only has values 0 or 1, then call it binary
        elif (np.logical_or(attributeDF[attrName]==0,attributeDF[attrName]==1).sum() == (attributeDF[attrName]).count()):
            binaries.append(attrName)
        else:
            continuouses.append(attrName)

    #create a dictionary to reference datatypes
    datatypeDict = {'bin':binaries,'cat':categoricals,'cont':continuouses}

    #return a corrected version of the datatype dictionary
    return checkForBinaryCategorical(attributeDF[datatypeDict['cat']],datatypeDict)

def read_nodes(filename):
    '''
    This reads in an x-y position file and stores in the
     'nodes' type data structure. Namely a dictionary
     of nodeId -> (x_pos,y_pos) , of strings pointing to tuples
    Code was copies from the drl_similarity function

    @param filename: the file from which to read.
    @return:
    '''
    # We want to read that.
    # This holds a reader for the DrL output
    # The last parm is a list of columns that should be floats
    coord_reader = tsv.TsvReader(open(filename, "r"), [1, 2])

    # This holds a dict from signature name string to (x, y) float tuple. It is
    # also our official collection of node names that made it through DrL, and
    # therefore need their score data sent to the client.
    nodes = {}

    print timestamp(), "Reading x-y positions..."
    sys.stdout.flush()
    for parts in coord_reader:
        nodes[parts[0]] = (parts[1], parts[2])
    coord_reader.close()

    # Return nodes dict back to main method for further processes
    return nodes

def timestamp():
    return str(datetime.datetime.now())[5:-7]

# Store global variables in one global context
class Context:
    def __init__(s):
        s.matrices = [] # Opened matrices files
        s.all_hexagons = {} # Hexagon dicts {layout0: {(x, y): hex_name, ...}, layout1: {(x, y): hex_name, ...}}
        s.binary_layers = [] # Binary layer_names in the first layout
        s.continuous_layers = [] # Continuous layer_names in the first layout
        s.categorical_layers = [] # categorical layer_names in the first layout
        s.sparse = []

    def printIt(s):
        print json.dumps(s, indent=4, sort_keys=True)

class InvalidAction(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def hexagon_center(x, y, scale=1.0):
    """
    Given a coordinate on a grid of hexagons (using wiggly rows in x), what is 
    the 2d Euclidian coordinate of its center?
    
    x and y are integer column and row coordinates of the hexagon in the grid.
    
    scale is a float specifying hexagon side length.
    
    The origin in coordinate space is defined as the upper left corner of the 
    bounding box of the hexagon with indices x=0 and y=0.
    
    Returns a tuple of floats.
    """
    # The grid looks like this:
    #
    #   /-\ /-\ /-\ /-\ 
    # /-\-/-\-/-\-/-\-/-\
    # \-/-\-/-\-/-\-/-\-/
    # /-\-/-\-/-\-/-\-/-\
    # \-/-\-/-\-/-\-/-\-/
    # /-\-/-\-/-\-/-\-/-\
    # \-/ \-/ \-/ \-/ \-/
    #   
    # Say a hexagon side has length 1
    # It's 2 across corner to corner (x), and sqrt(3) across side to side (y)
    # X coordinates are 1.5 per column
    # Y coordinates (down from top) are sqrt(3) per row, -1/2 sqrt(3) if you're 
    # in an odd column.
    
    center_y = math.sqrt(3) * y
    if x % 2 == 1:
        # Odd column: shift up
        center_y -= 0.5 * math.sqrt(3)
        
    return (1.5 * x * scale + scale, center_y * scale + math.sqrt(3.0) / 2.0 * 
        scale)

def hexagon_pick(x, y, scale=1.0):
    """
    Given floats x and y specifying coordinates in the plane, determine which 
    hexagon grid cell that point is in.
    
    scale is a float specifying hexagon side length.
    
    See http://blog.ruslans.com/2011/02/hexagonal-grid-math.html
    But we flip the direction of the wiggle. Odd rows are up (-y)
    """
    
    # How high is a hex?
    hex_height = math.sqrt(3) * scale
    
    # First we pick a rectangular tile, from the point of one side-traingle to 
    # the base of the other in width, and the whole hexagon height in height.
    
    # How wide are these tiles? Corner to line-between-far-corners distance
    tile_width = (3.0 / 2.0 * scale)
    
    # Tile X index is floor(x / )
    tile_x = int(math.floor(x / tile_width))
    
    # We need this intermediate value for the Y index and for tile-internal
    # picking
    corrected_y = y + (tile_x % 2) * hex_height / 2.0
    
    # Tile Y index is floor((y + (x index mod 2) * hex height/2) / hex height)
    tile_y = int(math.floor(corrected_y / hex_height))
    
    # Find coordinates within the tile
    internal_x = x - tile_x * tile_width
    internal_y = corrected_y - tile_y * hex_height
    
    # Do tile-scale picking
    # Are we in the one corner, the other corner, or the bulk of the tile?
    if internal_x > scale * abs(0.5 - internal_y / hex_height):
        # We're in the bulk of the tile
        # This is the column (x) of the picked hexagon
        hexagon_x = tile_x
        
        # This is the row (y) of the picked hexagon
        hexagon_y = tile_y
    else:
        # We're in a corner.
        # In an even column, the lower left is part of the next row, and the 
        # upper left is part of the same row. In an odd column, the lower left 
        # is part of the same row, and the upper left is part of the previous 
        # row.
        if internal_y > hex_height / 2.0:
            # It's the lower left corner
            # This is the offset in row (y) that being in this corner gives us
            # The lower left corner is always 1 row below the upper left corner.
            corner_y_offset = 1
        else:
            corner_y_offset = 0
            
        # This is the row (y) of the picked hexagon
        hexagon_y = tile_y - tile_x % 2 + corner_y_offset
        
        # This is the column (x) of the picked hexagon
        hexagon_x = tile_x - 1
    
    # Now we've picked the hexagon
    return (hexagon_x, hexagon_y)    

def radial_search(center_x, center_y):
    """
    An iterator that yields coordinate tuples (x, y) in order of increasing 
    hex-grid distance from the specified center position.
    """
    
    # A hexagon has neighbors at the following relative coordinates:
    # (-1, 0), (1, 0), (0, -1), (0, 1)
    # and ((-1, 1) and (1, 1) if in an even column)
    # or ((-1, -1) and (1, -1) if in an odd column)
    
    # We're going to go outwards using breadth-first search, so we need a queue 
    # of hexes to visit and a set of already visited hexes.
    
    # This holds a queue (really a deque) of hexes waiting to be visited.
    # A list has O(n) pop/insert at left.
    queue = collections.deque()
    # This holds a set of the (x, y) coordinate tuples of already-seen hexes,
    # so we don't enqueue them again.
    seen = set()
    
    # First place to visit is the center.
    queue.append((center_x, center_y))
    
    while len(queue) > 0:
        # We should in theory never run out of items in the queue.
        # Get the current x and y to visit.
        x, y = queue.popleft()
        
        # Yield the location we're visiting
        yield (x, y)
        
        # This holds a list of all relative neighbor positions as (x, y) tuples.
        neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if y % 2 == 0:
            # An even-column hex also has these neighbors
            neighbor_offsets += [(-1, 1), (1, 1)]
        else:
            # An odd-column hex also has these neighbors
            neighbor_offsets += [(-1, -1), (1, -1)]
    
        for x_offset, y_offset in neighbor_offsets:
            # First calculate the absolute position of the neighbor in x
            neighbor_x = x + x_offset
            # And in y
            neighbor_y = y + y_offset
            
            if (neighbor_x, neighbor_y) not in seen:
                # This is a hex that has never been in the queue. Add it.
                queue.append((neighbor_x, neighbor_y))
                
                # Record that it has ever been enqueued
                seen.add((neighbor_x, neighbor_y))

def assign_hexagon(hexagons, node_x, node_y, node, scale=1.0):
    """
    This function assigns the given node to a hexagon in hexagons. hexagons is a
    defaultdict from tuples of hexagon (x, y) integer indices to assigned nodes,
    or None if a hexagon is free. node_x and node_y are the x and y coordinates 
    of the node, adapted so that the seed node lands in the 0, 0 hexagon, and 
    re-scaled to reduce hexagon conflicts. node is the node to be assigned. 
    scale, if specified, is the hexagon side length in node space units.
    
    This function assigns nodes to their closest hexagon, reprobing outwards if 
    already occupied.
    
    When the function completes, node is stored in hexagons under some (x, y) 
    tuple.
    
    Returns the distance this hexagon is from its ideal location.
    """
    
    # These hold the hexagon that the point falls in, which may be taken.
    best_x, best_y = hexagon_pick(node_x, node_y, scale=scale)
    
    for x, y in radial_search(best_x, best_y):
        # These hexes are enumerated in order of increasign distance from the 
        # best one, starting with the best hex itself.
        
        if hexagons[(x, y)] is None:
            # This is the closest free hex. Break out of the loop, leaving x and
            # y pointing here.
            break
    
    # Assign the node to the hexagon
    hexagons[(x, y)] = node
    
    return math.sqrt((x - best_x) ** 2 + (y - best_y) ** 2)

def hexagons_in_window(hexagons, x, y, width, height):
    """
    Given a dict from (x, y) position to signature names, return the list of all
    signatures in the window starting at hexagon x, y and extending width in the
    x direction and height in the y direction on the hexagon grid.
    """        
    
    # This holds the list of hexagons we've found
    found = []
    
    for i in xrange(x, x + width):
        for j in xrange(y, y + height):
            if hexagons.has_key((i, j)):
                # This position in the window has a hex.
                found.append(hexagons[(i, j)])
                
    return found

def writeAndPutLayerDatatypes(datatypeDict, options, ctx):
    """
    This function writes the datatypes to the UI's data type file,
     and puts the data types into the ctx global
    @param datatypeDict:
    @param options:
    @return:
    """
    ctx.continuous_layers  = datatypeDict['cont']
    ctx.binary_layers      = datatypeDict['bin']
    ctx.categorical_layers = datatypeDict['cat']

    # Write the lists of continuous, binary, and categorical layers to files
    # The client side will use these to determine how to display values and
    # which layers to include when the user filters by data type.
    type_writer = tsv.TsvWriter(open(os.path.join(options.directory,
    "Layer_Data_Types.tab"), "w"))

    if (options.first_attribute):
        type_writer.line("FirstAttribute", options.first_attribute)
    type_writer.line("Continuous", *ctx.continuous_layers)
    type_writer.line("Binary", *ctx.binary_layers)
    type_writer.line("Categorical", *ctx.categorical_layers)

    type_writer.close()

    print timestamp(), 'Attribute counts:',' Binary:', len(ctx.binary_layers), '+ Categorical:', len(ctx.categorical_layers), '+ Continuous:', len(ctx.continuous_layers)

def open_matrices(names, ctx):
    """
    The argument parser now take multiple similarity matrices as input and
    saves their file name as strings. We want to store the names of these
    strings for display later in hexagram.js in order to allow the user to 
    navigate and know what type of visualization map they are looking at -
    gene expression, copy number, etc. 

    Since the parser no longer opens the files automatically we must, do it
    in this function.
    """
    # For each file name, open the file and add it to the matrices list
    # 'r' is the argument stating that the file will be read-only
    # swat: why are we opening the same file twice, once as a steam and once as
    # a std file where lines are added to ctx.sparse?
    for i, similarity_filename in enumerate(names):
        print 'Opening Matrix', i, similarity_filename
        
        matrix_file = tsv.TsvReader(open(similarity_filename, "r"))
        ctx.matrices.append(matrix_file)
        
        with open(similarity_filename,'r') as f:
            lines = [l.rstrip('\n') for l in f]

        ctx.sparse.append("\n".join(lines))

def extract_coords (axis, size, hexagons):
    """
    Extract the coordinate values for a certain set of hexagons.
    Then assign them to a numpy matrix, and return this matrix.
    """
    coords_matrix = np.zeros(shape=(size, 1))
    min_val = min(coords[axis] for coords in hexagons.iterkeys())

    index = 0
        
    for coords, name in hexagons.iteritems():
        val = coords[axis] - min_val
        val = val * 1
        coords_matrix[index, 0] = val
        index += 1
   
    return coords_matrix

def drl_similarity_functions(matrix, index, options):
    """
    Performs all the functions needed to format a similarity matrix into a 
    tsv format whereby the DrL can take the values. Then all of the DrL
    functions are performed on the similarity matrix.

    Options is passed to access options.singletons and other required aspects
    of the parsed args.

    @param matrix: most information for this layout
    @param index: index for this layout
    """

    print timestamp(), '============== Starting drl computations for layout:', \
          index, '... =============='
    
    # Work in a temporary directory
    # If not available, create the directory.
    drl_directory = tempfile.mkdtemp()
    
    # This is the base name for all the files that DrL uses to do the layout
    # We're going to put it in a temporary directory.
    # index added to extension in order to keep track of
    # respective layouts
    drl_basename = os.path.join(drl_directory, "layout" + str(index))

    # We can just pass our similarity matrix to DrL's truncate
    # But we want to run it through our tsv parser to strip comments and ensure
    # it's valid
    
    # This holds a reader for the similarity matrix
    sim_reader = matrix
    
    # This holds a writer for the sim file
    sim_writer = tsv.TsvWriter(open(drl_basename + ".sim", "w"))
    
    # This holds a list of all unique signature names in the similarity matrix.
    # We can use it to add edges to keep singletons.
    signatures = set()

    print "Reach for parts in sim_reader:" + str(sim_reader)

    for parts in sim_reader:
        # Keep the signature names used
        signatures.add(parts[0])
        signatures.add(parts[1])
        
        # Save the line to the regularized file
        sim_writer.list_line(parts)
    
    if options.singletons:
        # Now add a self-edge on every node, so we don't drop nodes with no
        # other strictly positive edges
        '''
        DCM012317 : it is unclear what this does to the DRL layout algorithm,
        however the flag seems to make the layouts more aesthetic.
        The argument was originally named --include-singletons, suggesting
         that new nodes may be included if the flag is raised. However,
         this code goes through all the nodes that are already present
         in the input and hence can not include something that isn't there.
         Note that DRL is an un-directed graph method, so directionality
          does not resolve the issue of including something that would
          otherwise not be present.
        '''
        for signature in signatures:
            sim_writer.line(signature, signature, 1)
        
    sim_reader.close()
    sim_writer.close()
    
    # Now our input for DrL is prepared!
    # Do DrL truncate.
    print timestamp(), "DrL: Truncating..."
    sys.stdout.flush()
    if options.drlpath:
        subprocess.check_call(["truncate", "-t", str(options.truncation_edges), 
            drl_basename], env={"PATH": options.drlpath},
            stdout=sys.stdout, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(["truncate", "-t", str(options.truncation_edges),
            drl_basename], stdout=sys.stdout,
                              stderr=subprocess.STDOUT)


    # Run the DrL layout engine.
    print "DrL: Doing layout..."
    sys.stdout.flush()
    if options.drlpath:
        subprocess.check_call(["layout", drl_basename], env={"PATH": options.drlpath},
            stdout=sys.stdout, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(["layout", drl_basename],
            stdout=sys.stdout, stderr=subprocess.STDOUT)

    # Put the string names back
    print timestamp(), "DrL: Restoring names..."
    sys.stdout.flush()
    if options.drlpath:
        subprocess.check_call(["recoord", drl_basename], env={"PATH": options.drlpath},
            stdout=sys.stdout, stderr=subprocess.STDOUT)
    else:
        subprocess.check_call(["recoord", drl_basename],
            stdout=sys.stdout, stderr=subprocess.STDOUT)
        
    # Now DrL has saved its coordinates as <signature name>\t<x>\t<y> rows in 
    # <basename>.coord


    # We want to read that.
    # This holds a reader for the DrL output
    coord_reader = tsv.TsvReader(open(drl_basename + ".coord", "r"))

    # This holds a dict from signature name string to (x, y) float tuple. It is
    # also our official collection of node names that made it through DrL, and
    # therefore need their score data sent to the client.
    nodes = {}

    print timestamp(), "Reading DrL output..."
    sys.stdout.flush()

    for parts in coord_reader:
        try:
            nodes[parts[0]] = (float(parts[1]), float(parts[2]))
        except IndexError:
            print "DRL has provided bad output, parts: ", parts
            raise

    coord_reader.close()

    # Delete our temporary directory.
    #shutil.rmtree(drl_directory)

    print timestamp(), '============== drl computations completed for layout:',\
          index, '=============='


    # Return nodes dict back to main method for further processes
    return nodes

def sideLength(maxX,maxY,minX,minY,n):
    """
    determines side lenght of a hexagon.
    rational here is that we'd like our hexagons to take up 5% of the space
    on the clustering plane.
    @param maxX: max of x in 2d clustering xy data
    @param maxY: max of y in 2d clustering xy data
    @param minX: min of x in 2d clustering xy data
    @param minY: min of Y in 2d clustering xy data
    @param n:    number of samples in 2d clustering xy data
    @return: float for side length of the hexagon
    """
    #this is the total area of the plane coming from the node assignments
    totalSpace = (maxX - minX) * (maxY - minY)

    #percent of space we'd like to take up
    PERCENTOFSPACE = .05
    RECIPRICALHEXCONST = (2/ (3*np.sqrt(3)))
    # area of a regular hex is sqrt(3)*3/2 * side^2
    # so the side length we'd like for our hexs to take up 5% of the space
    # is:
    side = np.sqrt(totalSpace * PERCENTOFSPACE * RECIPRICALHEXCONST* (
        1/float(n)))

    return side

def compute_hexagram_assignments(nodes, index, options, ctx):
    """
    Now that we are taking multiple similarity matrices as inputs, we must
    compute hexagram assignments for each similarity matrix. These assignments 
    are based up on the nodes output provided by the DrL function. 

    Index relates each matrix name with its drl output, nodes, assignments, etc.
    Options contains the parsed arguments that are present in the main method.
    
    Returns the placement badness for the layout with the given index, and saves
    the hexagon assignment dict in the global all_hexagons dict under the layer
    index.
    
    """

    # Write out the xy coordinates before squiggling. First find the x and y
    # offsets needed to make all hexagon positions positive
    min_x = min_y = max_x = max_y = None
    count=0
    for name, coords in nodes.iteritems():
        count+=1
        if min_x is None:
            min_x = coords[0]
            min_y = coords[1]
            max_x = coords[0]
            max_y = coords[1]
        else:
            min_x = min(min_x, coords[0])
            min_y = min(min_y, coords[1])
            max_x = max(max_x, coords[0])
            max_y = max(max_y, coords[1])


    node_writer = tsv.TsvWriter(open(os.path.join(options.directory, "xyPreSquiggle_"+ str(index) + ".tab"), "w"))

    # Write this file header.
    node_writer.line('#ID', 'x', 'y')

    # Write the node names with coordinates converted to all-positive.
    for name, coords in nodes.iteritems():
        node_writer.line(name, coords[0] - min_x, coords[1] - min_y)
    node_writer.close()

    # Do the hexagon layout
    # We do the squiggly rows setup, so express everything as integer x, y
    
    # This is a defaultdict from (x, y) integer tuple to id that goes there, or
    # None if it's free.
    hexagons = collections.defaultdict(lambda: None)

    # get side length that we want to:
    # if we are using DRL assume that 1 is a good side length (it has worked so
    # far without complaint :)

    #figure out whether we have an xy entry
    xyEntry = False
    try:
        xyEntry = len(options.coordinates) > 0
    except TypeError:
        xyEntry = options.layoutInputFormat == "xyPositions"

    if xyEntry: #some other method is providing xy data
        # we'd like hexagons to be 5% of the taken up space
        side_length = sideLength(max_x,max_y,min_x,min_y,count)
        print "x-y input: hexagon side length chosen as " + str(side_length)

    else: # we are using OpenOrd and this side length works well with the
          # scaling
        side_length = 1.0
    # This holds what will be a layer of how badly placed each hexagon is
    # A dict from node name to layer value
    placement_badnesses = {}

    for node, (node_x, node_y) in nodes.iteritems():
        # Assign each node to a hexagon
        # This holds the resulting placement badness for that hexagon (i.e. 
        # distance from ideal location)
        badness = assign_hexagon(hexagons, node_x, node_y, node,
            scale=side_length)
            
        # Put the badness in the layer
        placement_badnesses[node] = float(badness)
   
    # Normalize the placement badness layer
    # This holds the max placement badness
    max_placement_badness = max(placement_badnesses.itervalues())
    if DEV:
        print "Max placement badness: {}".format(max_placement_badness)

    if max_placement_badness != 0:
        # Normalize by the max if possible.
        placement_badnesses = {node: value / max_placement_badness for node, 
            value in placement_badnesses.iteritems()}
   
    # The hexagons have been assigned. Make hexagons be a dict instead of a 
    # defaultdict, so it pickles.
    hexagons = dict(hexagons) 

    # Add this dict of hexagons to all_hexagons dict, so it can be used later
    # for statistics.
    ctx.all_hexagons[index] = hexagons

    # Now dump the hexagon assignments as an id, x, y tsv. This will be read by
    # the JavaScript on the static page and be used to produce the 
    # visualization.        
    hexagon_writer = tsv.TsvWriter(open(os.path.join(options.directory, 
        "assignments"+ str(index) + ".tab"), "w"))

    # First find the x and y offsets needed to make all hexagon positions 
    # positive
    min_x = min(coords[0] for coords in hexagons.iterkeys())
    min_y = min(coords[1] for coords in hexagons.iterkeys())  
        
    for coords, name in hexagons.iteritems():
        # Write this hexagon assignment, converted to all-positive coordinates.
        hexagon_writer.line(name, coords[0] - min_x, coords[1] - min_y)    
    hexagon_writer.close()

    # Hand placement_badness dict to main method so that it can be sent to the
    # client. The hexagon assignment dict has already been saved in
    # all_hexagons.
    return placement_badnesses
                
def write_similarity_names(options):
    """
    Write the human names and file names of the similarity matrices so that 
    the tumor map UI can use them.
    """    
    with open(os.path.join(options.directory, 'layouts.tab'), 'w') as f:
        f = csv.writer(f, delimiter='\t', lineterminator='\n')
        for i, name in enumerate(options.names):
            f.writerow([name])

def inferringFormat(options):
    return options.layoutInputFile is not None

def writeMetaData(options):

    inferring_format = inferringFormat(options)
    # Store some metadata in the meta.json file for map group info like role and
    # into mapMeta.json for map-specific info like clustering data file path.
    #
    # If this is called via docker's CWL or via CLI we don't know the data
    # directory structure and must make some assumptions and so the meta data
    # file(s) may be incorrect. We expect these users to be more sophistocated
    # and know about how to fix up the meta data.
    # When called via the web API we set the data directory structure so the
    # meta data is reliable.
    
    # Find the base map name, without the optional mapGroup.
    mapBaseI = string.rfind(options.directory[:-1], '/') + 1
    mapBase = options.directory[mapBaseI:]

    # Start off assuming no mapGroup so it is the same dir as the base map.
    mapGroupDir = options.directory
    mapGroup = mapBase
    
    # Find the parent name.
    parentI = string.rfind(options.directory[:mapBaseI-1], '/') + 1
    parent = options.directory[parentI:mapBaseI-1]
    
    if parent != 'view':
    
        # The parent is either the map group or this is not our standard data
        # directory structure.

        # Find the grandparent name
        gParentI = string.rfind(options.directory[:parentI-1], '/') + 1
        gParent = options.directory[gParentI:parentI-1]
        if gParent == 'view':\
        
            # This is our standard data directory structure with a mapGroup.
            mapGroup = options.directory[parentI:mapBaseI-1]
            mapGroupDir = options.directory[:mapBaseI-1]

    # Save the map group meta data if there is any.
    if options.role:
        
        # Open any existing meta.json file and load its meta data.
        metaPath = os.path.join(mapGroupDir, 'meta.json')
        meta = {}
        try:
            with open(metaPath, 'r') as f:
                meta = json.load(f)
                
        except:
            # No meta.json file yet.
            pass
        
        # TODO make this write to an array of roles rather than a single
        # value. For now do not overwrite any existing role
        if 'role' not in meta:
            meta['role'] = options.role
        
        try:
            with open(metaPath, 'w') as f:
                json.dump(meta, f, indent=4)
        except:
            # We assume we could not write to this dir because this was called
            # via CWL/CLI and the directory is protected.
            print('Warning: could not write meta.json file')
                
    # Save the base-map-specific meta data if there are any. This is for
    # operations like placing new nodes or sub-maps.
    if options.feature_space:

        # Build the meta data for each layout. Paths written are relative to the
        # data root so may not be reliable when called via CWL/CLI where we
        # don't know the data root.
        meta = { 'layouts': {} }
        metaPath = os.path.join(options.directory, 'mapMeta.json')
        for i, name in enumerate(options.names):
        
            # We only save this data if our standard data directory structure
            # created with the web API is being used. We do the best we can by
            # looking for 'featureSpace' in the layoutInput file name.
            if inferring_format:
                # In this case that position is a dataframe
                # The name of the file is in the index name.
                j = options.feature_space[i].index.name.find('featureSpace')
            else:
                j = options.feature_space[i].find('featureSpace')

            if j < 0:
                continue

            # Save the file name relative to the data root
            if inferring_format:
                meta['layouts'][name] = {'clusterData': options.feature_space[i].index.name[j:]}
            else:
                meta['layouts'][name] = {'clusterData': options.feature_space[i][j:]}

        meta["nodeIdSearchUrl"] = options.nodeIdSearchUrl
        # Write the json file
        with open(metaPath, 'w') as f:
            json.dump(meta, f, indent=4)

def copy_files_for_UI(options, layer_files, layers, layer_positives, clumpiness_scores):
    """
    Copy some files over to the view space so it may access them.
    """
    # Write an index of all the layers we have, in the form:
    # <layer>\t<file>\t<number of signatures with data>\t<number of signatures
    # that are 1 for binary layers, or NaN> and then columns with the clumpiness
    # score for each layout.

    #if we use the new density, then layers.tab is printed else where.
    # namely leesL.writeLayersTab()
    if not options.clumpinessStats or not len(layers) > 1:
        # This is the writer to use.
        index_writer = tsv.TsvWriter(open(os.path.join(options.directory,
            "layers.tab"), "w"))

        print "Writing layer index..."

        for layer_name, layer_file in layer_files.iteritems():
            # Gather together the parts to write
            parts = [layer_name, os.path.basename(layer_file),
                len(layers[layer_name]), layer_positives[layer_name]]

            for clumpiness_dict in clumpiness_scores:
                # Go through each dict of clumpiness scores by layer, in layout
                # order, and put the score for this layer in this layout at the end
                # of the line.

                parts.append(clumpiness_dict[layer_name])

            # Write the index entry for this layer
            index_writer.list_line(parts)

        index_writer.close()

    # Copy over the tags file if one exists
    if options.attributeTags is not None:
        tagsPath = os.path.join(options.directory, 'attribute_tags.tab')
        shutil.copy(options.attributeTags, tagsPath)
        print 'Tags file copied to', tagsPath

    if options.feature_space or options.role:
        writeMetaData(options)
    
def build_default_scores(options):

    # Build a fake scores file from the node IDs in the first layout. This is a
    # hack to get around the server code expecting at least one layer.
    
    file_name = options.directory + '/fake_layer.tab'
    with open(file_name, 'w') as fout:
        fout = csv.writer(fout, delimiter='\t')
        fout.writerow(['s1', 0.1])
        fout.writerow(['s2', 0.2])
        fout.writerow(['s3', 0.3])
    #options.scores = ['fake_layer_0', 'fake_layer_1']
    return file_name

def getDefaultOpts():
    '''
    @return: dictionary of default opts
    '''
    defaults = parse_args([]).__dict__
    """
    This shows the results of the above parse_args([]).__dict__ call on
    03172016. It will change as argparse changes. Note that the key is the
    "dest"
      param of the arg defenition in arg_parse, and the value is the "default"
    defaults = {'associations': True, #bool
                'attributeTags': None, #string filepath
                'clumpinessStats': True, #boolean
                 'colormaps': '', #string filepath, empty if omitted
                 'coordinates': None, #[[path,path,path]]
                 'directedGraph': True, #bool
                 'directory': '.', #string filepath
                 'drlpath': None, #string filepath
                 'feature_space': None, #[[path,path,path]]
                 'first_attribute': '', sting filepath, empty if omitted
                 'metric': None, [[metric,metric,metric]]
                 'mutualinfo': True, #bool
                 'names': [], #[string,string,...]
                 'output_tar': '', #string filepath
                 'output_zip': '', #string filepath
                 'rawsim': None, #deprecated
                 'role': None, #string specifying meaningful role description
                 'scores': None, #[path,path,path,...]
                 'similarity': None, #[[path,path,path,...]]
                 'similarity_full': None, #[[path,path,path,...]]
                 'singletons': False, #bool
                 'truncation_edges': 6, #int
                 'type': None, #deprecated
                 }

    """
    return defaults

def tete_wrapper(dt, col_names, neighborCount):
    """Import and call tete with output expected by rest of pipeline."""
    nodes = {}
    try:
        from tete import teter
        xys = teter(dt, 2, neighborCount)
        for i in range(xys.shape[0]):
            nodes[col_names[i]] = (xys[i,0], xys[i,0])
        return nodes
    except ImportError:
        raise ImportError("tete algorithm not available on this machine,"
                          " python path is: \n" + str(sys.path))

def fillOpts(options):
    '''
    fills in default options if not present
    @param options: arg parse Namespace object
    @return: modified "options" Namespace object
    '''

    #grab default options as a dict
    defaults = getDefaultOpts()

    #namespace class is mutable through vars(), like options.__dict__
    optionsDict = vars(options)

    #fill in defaults
    for needed in defaults.keys():
        try:
            optionsDict[needed]
        except KeyError:
            optionsDict[needed] = defaults[needed]

    # Override some options that have become constants.
    options.clumpinessStats = True
    options.directedGraph = True
    options.singletons = True

    # Handle input layout parameters
    operatingVars = \
        ['feature_space', 'similarity_full', 'similarity', 'coordinates']

    if options.layoutInputFile is None:

        # Using the deprecated parameters so they are already mapped to the
        # operating variables. Only allow one format and ignore the rest.
        formats = filter(lambda x: getattr(options, x), operatingVars)
        
        if len(formats) < 1:
            raise ValueError("One of these feature layout options " +
                "must be specified: feature_space similarity, " +
                "similarity_full, coordinates.")
        theFormat = formats[0]

        # Keep the first format encountered and clear the rest.
        for format in operatingVars:
            if format != theFormat:
                setattr(options, format, None)

    return options

def makeMapUIfiles(options, cmd_line_list=None):
    '''
    main function, contains entire pipeline for Tumor Map generation
    :param options: parse args namespace object, see getDefaultOpts() for a
                    dictionary of defaults of the needed object attributes
    :param cmd_line_list: the commands parsed off of the command line
    :return: None, writes out a plethora of needed files to a directory specified in 'options'
    '''

    #make sure the common defaults are in the options Namespace
    givenOptions = options
    options = fillOpts(options)

    #make the destination directory for output if its not there
    if not os.path.exists(options.directory):
        os.makedirs(options.directory)

    #Set stdout and stderr to a log file in the destination directory
    log_file_name = options.directory + '/log'
    stdoutFd = sys.stdout
    sys.stdout = open(log_file_name, 'w')
    sys.stderr = sys.stdout

    if cmd_line_list:
        print timestamp(), 'Started'
        print 'command-line options:'
        #print out each arg on its own line
        print '\n'.join(cmd_line_list)

    #print all the options given to the log.
    print 'all given options:'
    pprint.pprint(givenOptions.__dict__)

    #print all the options after adjustment to the log.
    print 'all adjusted options:'
    pprint.pprint(options.__dict__)
    sys.stdout.flush()

    # Check if we are computationally verifying the
    # "layoutInputFormat".
    inferring_format = inferringFormat(options)
    if inferring_format:
        more_than_one = False
        for fin in options.layoutInputFile:
            df = utils.readPandas(fin)
            inferred_format= formatCheck._layoutInputFormat(df)
            if more_than_one:
                assert inferred_format == last_inferred_format
            #two cases where we really don't want to read in data twice
            if inferred_format == "clusterData":
                if not more_than_one:
                    options.feature_space = []
                if options.zeroReplace:
                    df= df.fillna(0)
                options.feature_space.append(df)

            elif inferred_format == "fullSimilarity":
                if not more_than_one:
                    options.similarity_full = []

                options.similarity_full.append(df)

            elif inferred_format == "sparseSimilarity":
                if not more_than_one:
                    options.similarity= []
                options.similarity.append(fin)

            elif inferred_format == "xyPositions":
                if not more_than_one:
                    options.coordinates= []
                options.coordinates.append(fin)

            more_than_one = True
            last_inferred_format = inferred_format

        print "inferred_format was: " + inferred_format
    #####

    ctx = Context()

    #javascript expects at least one attribute so put something fake there
    # if none exist
    if options.scores == None:
        options.scores = [build_default_scores(options)]

    #if no colormaps file is specified then assume it needs to be created
    # and annotations need to be converted to tumor map mappings.
    # If attributes are not specified then there is no colormap to create.
    if not(options.scores == None):

        create_colormaps_file(options.scores,os.path.join(options.directory,'colormaps.tab'),
                              colormaps=options.colormaps,
                              attrsfile=os.path.join(options.directory,'allAttributes.tab')
                              )
        options.scores = [os.path.join(options.directory,'allAttributes.tab')]
        options.colormaps = os.path.join(options.directory,'colormaps.tab')

    # Set some global context values
    ctx.extract_coords = extract_coords
    ctx.timestamp = timestamp

    # Test our picking
    x, y = hexagon_center(0, 0)
    if hexagon_pick(x, y) != (0, 0):
        raise Exception("Picking is broken!")

    print "Writing matrix names..."
    #write the option,names out,
    # options.names is a human readable description of the data used to create
    # the 2 dimensional clustering
    write_similarity_names(options)
    
    # The nodes list stores the list of nodes for each matrix
    # We must keep track of each set of nodes
    nodes_multiple = []
    print "Created nodes_multiple list..."

    print "About to open matrices..."

    # We have file names stored in options.similarity
    # We must open the files and store them in matrices list for access
    if not(options.coordinates == None): #TODO: x-y pos should be a way for reproducing maps
        for i, coords_filename in enumerate(options.coordinates):
            nodes = read_nodes(coords_filename)
            nodes_multiple.append(nodes)
            ctx.sparse=[]

    else:
        if options.layoutMethod.upper() == "TETE":
            for i, genomic_filename in enumerate(options.feature_space):
                    if inferring_format:
                        # "Genomic filename is actually a pandas dataFrame
                        dt, sample_labels, feature_labels = \
                            compute_sparse_matrix.pandasToNumpy(genomic_filename)
                    else:
                        dt, sample_labels, feature_labels = \
                            read_tabular(genomic_filename,
                                         True,
                                         replaceNA=options.zeroReplace
                                         )
                    if options.doingRows:
                        # Swap the sample and feature labels and continue
                        sample_labels, feature_labels = \
                            feature_labels, sample_labels
                    else:
                        dt = dt.transpose()

                    nodes_multiple.append(tete_wrapper(dt,
                                                       sample_labels,
                                                options.truncation_edges))

            options.coordinates = True

        else:    #'DRL'
            print 'DRL method'
            if not (options.feature_space == None):    #full feature space matrix given
                print "Feature matrices"
                for i, genomic_filename in enumerate(options.feature_space):

                    if inferring_format:
                        # "Genomic filename is actually a pandas dataFrame
                        dt, sample_labels, feature_labels = \
                            compute_sparse_matrix.pandasToNumpy(genomic_filename)
                    else:
                        dt, sample_labels, feature_labels = \
                            read_tabular(genomic_filename,
                                         True,
                                         replaceNA=options.zeroReplace
                                         )

                    print str(len(dt))+" x "+str(len(dt[0]))
                    if options.doingRows:
                        # Swap the sample and feature labels and continue
                        sample_labels, feature_labels = \
                            feature_labels, sample_labels
                    else:
                        dt = np.transpose(dt)

                    result = sparsePandasToString(compute_similarities(dt=dt, sample_labels=sample_labels, metric_type=options.distanceMetric, num_jobs=12, output_type="SPARSE", top=options.truncation_edges, log=None))
                    result_stream = StringIO.StringIO(result)
                    matrix_file = tsv.TsvReader(result_stream)
                    ctx.matrices.append(matrix_file)
                    ctx.sparse.append(result)

            elif not (options.similarity_full == None):    #full similarity matrix given
                print "Similarity matrices"
                for i, similarity_filename in enumerate(options.similarity_full):
                    print 'Opening Matrix', i, similarity_filename

                    if inferring_format:
                        # "similarity filename is actually a pandas dataFrame
                        dt, sample_labels, feature_labels = \
                            compute_sparse_matrix.pandasToNumpy(similarity_filename)
                    else:
                        dt,sample_labels,feature_labels = \
                            read_tabular(similarity_filename,
                                         True,
                                         replaceNA=options.zeroReplace
                                         )

                    print str(len(dt))+" x "+str(len(dt[0]))
                    result = sparsePandasToString(extract_similarities(dt=dt, sample_labels=sample_labels, top=options.truncation_edges, log=None))
                    result_stream = StringIO.StringIO(result)
                    matrix_file = tsv.TsvReader(result_stream)
                    ctx.matrices.append(matrix_file)
                    ctx.sparse.append(result)
            
            elif not (options.similarity == None):        #sparse similarity matrix given
                print "Sparse similarity matrices"
                open_matrices(options.similarity, ctx)
                print options.similarity
            elif not(options.coordinates == None):
                #do nothing.
                '''already have x-y coords so don't need to do anything.'''
            else:    #no matrix is given
                raise InvalidAction("Invalid matrix input was provided")
            
            # Index for drl.tab and drl.layout file naming. With indexes we can match
            # file names, to matrices, to drl output files.
            #print "length of ctx.matrices = "+str(len(ctx.matrices))
            # if we have x-ys then we don't need to do drl.
            if (options.coordinates == None):
                for index, i in enumerate (ctx.matrices):
                    print "enumerating ctx.matrices "+str(index)
                    nodes_multiple.append(drl_similarity_functions(i, index, options))

    print "Opened matrices..."
    #print nodes_multiple
    #print len(nodes_multiple[0])
    #print nodes_multiple
    
    # Index for drl.tab and drl.layout file naming. With indexes we can match
    # file names, to matrices, to drl output files.
    #print "length of ctx.matrices = "+str(len(ctx.matrices))
    #for index, i in enumerate (ctx.matrices):
    #    print "enumerating ctx.matrices "+str(index)
    #    nodes_multiple.append (drl_similarity_functions(i, index, options))
    #print "nodes_multiple:"
    #print nodes_multiple

    # Compute Hexagam Assignments for each similarity matrix's drl output,
    # which is found in nodes_multiple.

    # placement_badnesses_multiple list is required to store the placement
    # badness dicts that are returned by the compute_hexagram_assignments
    # function. compute_hexagram_assignments will also fill in the all_hexagons
    # dict for each layout it processes, so we can get hexagon assignments for
    # those layouts when we go to do statistics.
    placement_badnesses_multiple = []
    for index, i in enumerate(nodes_multiple):
        # Go get the placement badness
        placement_badness = compute_hexagram_assignments(i, index, options, ctx)

        # Record the placement badness under this layout.
        placement_badnesses_multiple.append(placement_badness)

    # Now that we have hex assignments, compute layers.
    
    # In addition to making per-layer files, we're going to copy all the score
    # matrices to our output directory. That way, the client can download layers
    # in big chunks when it wants all layer data for statistics. We need to
    # write a list of matrices that the client can read, which is written by
    # this TSV writer.
    matrix_index_writer = tsv.TsvWriter(open(os.path.join(options.directory, 
        "matrices.tab"), "w"))
        
    # Read in all the layer data at once

    # This holds a dict from layer name to a dict from signature name to 
    # score.
    layers = {}
    
    # This holds the names of all layers
    # TODO they should hold those layers with at least one value
    layer_names = []
    
    for matrix_number, score_filename in enumerate(options.scores):
        # First, copy the whole matrix into our output. This holds its filename.
        output_filename = "matrix_{}.tab".format(matrix_number)
        shutil.copy(score_filename, os.path.join(options.directory, 
            output_filename))
            
        # Record were we put it
        matrix_index_writer.line(output_filename)
    
        # This holds a reader for the scores TSV
        scores_reader = tsv.TsvReader(open(score_filename, "r"))
        
        # This holds an iterator over lines in that file
        # TODO: Write a proper header/data API
        scores_iterator = scores_reader.__iter__()

        try:
            # This holds the names of the columns (except the first, which is 
            # labels). They also happen to be layer names
            file_layer_names = scores_iterator.next()[1:]
            
            # Add all the layers in this file to the complete list of layers.
            layer_names += file_layer_names
            
            # Ensure that we have a dict for every layer mentioned in the file
            # (even the ones that have no data below). Doing it this way means
            # all score matrices need disjoint columns, or the last one takes
            # precedence.
            for name in file_layer_names:
                layers[name] = {} 
            
            for parts in scores_iterator:
                # This is the signature that this line is about
                signature_name = parts[0]
                
                # Check all nodes for signature name. Not just the first node.
                missing_from_subset = 0
                for node_subset in nodes_multiple:
                    if signature_name not in node_subset:
                        missing_from_subset += 1
                
                if missing_from_subset == len (nodes_multiple):
                    # This signature wasn't in our DrL output. Don't bother
                    # putting its layer data in our visualization. This saves
                    # space and makes the client-side layer counts accurate for
                    # the data actually displayable.
                    continue

                # These are the scores for all the layers for this signature
                layer_scores = parts[1:]
                
                for (layer_name, score) in itertools.izip(file_layer_names, 
                    layer_scores):

                    # Store all the layer scores in the appropriate
                    # dictionaries.
                    try:
                        layers[layer_name][signature_name] = float(score)
                    except ValueError:
                        # This is not a float.
                        # Don't set that entry for this layer.
                        # TODO: possibly ought to complain to the user? But then
                        # things like "N/A" won't be handled properly.
                        continue
                    
        except StopIteration:
            # We don't have any real data here. Couldn't read the header line.
            # Skip to the next file
            pass
            
        # We're done with this score file now
        scores_reader.close()

    # We're done with all the input score matrices, so our index is done too.
    matrix_index_writer.close()

    if DEV:
        # Stick our placement badness layer on the end
        layer_names.append("Placement Badness")
        layers["Placement Badness"] = placement_badnesses_multiple[0]

    # Report multiple attribute name instances in layer_names list
    dupAttrs = []
    for name in layers.keys():
        count = layer_names.count(name)
        if count > 1:
            dupAttrs.append([name, count])
    if len(dupAttrs) > 0:
        print 'ERROR: multiple instances of attributes:', dupAttrs
        raise Exception('ERROR: multiple instances of attributes!')

    # Now we need to write layer files. First remove any empty layers from
    # layer_names and the layer dict. This means there will never be a break
    # in sequential indices when naming files, and following code will not have
    # to handle the case of an empty layer file
    # TODO For some reason a layer_names may not be in layers, and a layers name
    # may not be in layer_names. Fix it to avoid issues down the line
    empty_layers = set()
    for name in layers.keys():
        if len(layers[name]) == 0:
            del layers[name]
            layer_names.remove(name)
            empty_layers.add(name)
    if len(empty_layers) > 0:
        print 'WARNING: No values in these layers:', list(empty_layers)

    # Generate some filenames for layers that we can look up by layer index.
    # We do this because layer names may not be valid filenames.
    layer_files = {name: os.path.join(options.directory, 
        "layer_{}.tab".format(number)) for (name, number) in itertools.izip(
        layer_names, itertools.count())}

    for layer_name, layer in layers.iteritems():
        # Write out all the individual layer files
        # This holds the writer for this layer file
        scores_writer = tsv.TsvWriter(open(layer_files[layer_name], "w"))
        for signature_name, score in layer.iteritems():
            # Write the score for this signature in this layer
            scores_writer.line(signature_name, sigDigs(score))
        scores_writer.close()

    # We send "clumpiness scores" for each layer to the client (greater is
    # clumpier), if the user has elected to spend the long amount of time it
    # takes to calculate them.
    
    # This holds a list of dicts of clumpiness scores by layer, ordered by
    # layout.
    #this is an array filled with pandas Series describing the density for each layout.
    densityArray = []
    clumpiness_scores = []

    datatypeDict = {'bin':[],'cat':[],'cont':[]}
    nlayouts = len(nodes_multiple)
    # Determine Data Type
    if len(layer_names) > 0:
        attrDF = getAttributes(options.scores)
        datatypeDict = getDataTypes(attrDF,options.directory + '/colormaps.tab')
        leesL.writeDummyLayersTab(layer_files,layers,
                                  attrDF, datatypeDict,
                                  nlayouts, options.directory
                                  )
    #puts the datatypes in the global object and writes them to the UI file
    writeAndPutLayerDatatypes(datatypeDict, options, ctx)



    if len(layer_names) > 1 and options.clumpinessStats:
        ###############################DCM121916###################################3
        #calculates density using the Lees'L method

        for index in range(nlayouts):
            print 'calculating density for layer ' + str(index)
            xys = utils.readXYs(options.directory + '/xyPreSquiggle_' + str(
                index)+'.tab')
            densityArray.append(leesL.densityOpt(attrDF,datatypeDict,xys,debug=True))

        leesL.writeLayersTab(attrDF,layers,layer_files,densityArray,datatypeDict,options)
        ###########################################################################3
    else:
        #We aren't doing any stats.
        ##DCM 011017:
        ##Note that the cases below run the same command, and therefor are superfluous in the
        ##case when the input is standardized.
        print "Skipping density statistics."
        if not (options.feature_space == None):    #full feature matrix given
            # Set everything's clumpiness score to -inf.
            clumpiness_scores = [collections.defaultdict(lambda: float("-inf"))
                for _ in options.feature_space]
        elif not (options.similarity_full == None):    #full similarity matrix given
            # Set everything's clumpiness score to -inf.
            clumpiness_scores = [collections.defaultdict(lambda: float("-inf"))
                for _ in options.similarity_full]
        elif not (options.similarity == None):        #sparse similarity matrix given
            # Set everything's clumpiness score to -inf.
            clumpiness_scores = [collections.defaultdict(lambda: float("-inf"))
                for _ in options.similarity]
        elif not (options.coordinates == None):
            # Set everything's clumpiness score to -inf.
            clumpiness_scores = [collections.defaultdict(lambda: float("-inf"))
                for _ in options.coordinates]
        else:    #no matrix is given
            raise InvalidAction("Invalid matrix input was provided")

    # Count how many layer entries are greater than 0 for each binary layer, and
    # store that number in this dict by layer name. Things with the default
    # empty string instead of a number aren't binary layers, but they can use
    # the empty string as their TSV field value, so we can safely pull any layer
    # out of this by name.
    layer_positives = collections.defaultdict(str)

    for layer_name in layer_names:
        if layer_name in ctx.binary_layers:
            layer_positives[layer_name] = 0
            for value in layers[layer_name].itervalues():
                if value == 1:
                    # Count up all the 1s in the layer
                    layer_positives[layer_name] += 1
                elif value != 0:
                    # It has something that isn't 1 or 0, so it can't be a binary
                    # layer. Throw it out and try the next layer.
                    layer_positives[layer_name] = ""
                    break
        else:
            layer_positives[layer_name] = ""

    copy_files_for_UI(options, layer_files, layers, layer_positives, clumpiness_scores)

    '''
    DCM Note : TODO: The file hexNames
    is misleading because hexnames only has the node ID's for one layer
     and there is often new nodes in different datatypes, which is a common use case for
     multiple layouts.
    '''
    # Create the hex names file accessed by the stats subprocesses,
    # even if we don't pre-compute stats, do this for dynamic  stats
    hexNames = ctx.all_hexagons[0].values()
    with open(os.path.join(options.directory, 'hexNames.tab'), 'w') as f:
        f = csv.writer(f, delimiter='\t')
        for name in hexNames:
            f.writerow([name])

    # Run pairwise meta data stats
    if options.associations:
        print 'layout independent stats starting'
        indstats_time = time.time()
        statsNoLayout(layers, layer_names, ctx, options)
        #new optimized function for computing stats.
        # testing on Pancan12 soon.
        #runAllbyAllForUI(options.directory,leesL.readLayers(options.directory+'\layers.tab'),attrDF, dataTypeDict)
        mins_taken = (time.time() - indstats_time) / 60.0
        print 'layout independent stats finished in ' + str(mins_taken) + ' minutes'
    else:
        print 'Skipping sort stats without layout (sample-based)'

    '''
    this is replaced by the leesL method for doing layout-aware stats
    # Run region-based stats
    # Call this no matter if these stats were requested or not so that the
    # Sampling windows are built in case the user requests a dynamic stats
    # from the viz UI.
    statsLayout(options.directory, layers, layer_names, nodes_multiple, ctx, options)
    '''

    #need at least two attribures to do mutual info
    if (options.mutualinfo and len(layer_names) > 1):
        print 'LeesL layout aware stats being calculated'

        #subset down  to binary attributes
        binAttrDF= attrDF[datatypeDict['bin']]

        #need to get layers file to know the indecies used for the outputted filenames
        layers = leesL.readLayers(options.directory + '/layers.tab')

        for index in range(len(nodes_multiple)):
            xys = utils.readXYs(options.directory + '/xyPreSquiggle_' + str(
                index)+'.tab')

            #filter and preprocess the binary attributes on the map
            attrOnMap = leesL.attrPreProcessing4Lee(binAttrDF,xys)
            # attributes ar e
            leeMatrix = leesL.leesL(leesL.spatialWieghtMatrix(xys),attrOnMap)
            #take all pairwise correlations of Binaries to display along with Lees L
            corMat=1-sklp.pairwise_distances(attrOnMap.transpose(),metric='correlation',n_jobs=8)

            leesL.writeToDirectoryLee(options.directory + '/',leeMatrix,corMat,attrOnMap.columns.tolist(),layers,index)

    # Find the top neighbors of each node.
    # TODO This is only running to produce the directed graph data,
    # 'neighbors_*.tab' to display the node density view. Seems like this is
    # redundant.
    if not(options.coordinates == None):
        for index, i in enumerate(ctx.sparse):
            topNeighbors_from_sparse(ctx.sparse[index], options.directory, options.truncation_edges, index)
    else:
        if options.layoutMethod.upper() in ['TSNE', 'MDS', 'PCA', 'ICA', 'ISOMAP', 'SPECTRALEMBEDDING']:
                if options.directedGraph:
                    #topNeighbors(options.feature_space, options.directory, options.truncation_edges)
                    for index, i in enumerate(ctx.sparse):
                        topNeighbors_from_sparse(ctx.sparse[index], options.directory, options.truncation_edges, index)
        else:    #'DRL'
            if not (options.feature_space == None):    #full feature space matrix given
                if options.directedGraph:
                    #topNeighbors(options.feature_space, options.directory, options.truncation_edges)
                    for index, i in enumerate(ctx.sparse):
                        topNeighbors_from_sparse(ctx.sparse[index], options.directory, options.truncation_edges, index)
            elif not (options.similarity_full == None):    #full similarity matrix given
                if options.directedGraph:
                    #topNeighbors(options.similarity_full, options.directory, options.truncation_edges)
                    for index, i in enumerate(ctx.sparse):
                        topNeighbors_from_sparse(ctx.sparse[index], options.directory, options.truncation_edges, index)
            elif not (options.similarity == None):        #sparse similarity matrix given
                if options.directedGraph:
                    topNeighbors(options.similarity, options.directory, options.truncation_edges)
                    for index, i in enumerate(ctx.sparse):
                        topNeighbors_from_sparse(ctx.sparse[index], options.directory, options.truncation_edges, index)
            else:    #no matrix is given
                raise InvalidAction("Invalid matrix input was provided")

    print timestamp(), "Visualization generation complete!"
    
    if len(options.output_zip) > 0:
        print "Writing the output to a zip file "+options.output_zip
        import zipfile
        zip_name = zipfile.ZipFile(options.output_zip, 'w',zipfile.ZIP_DEFLATED)
        for file in glob.glob(os.path.join(options.directory, "*")):
            zip_name.write(file, os.path.basename(file))
        zip_name.close()
        print "Done writing a zip file"
    
    if len(options.output_tar) > 0:	#note that possible to both tar and zip by specifying different output files for each
        print "Writing the output to a tar file "+options.output_tar
        import tarfile
        with tarfile.open(options.output_tar, "w:gz") as tar:
            tar.add(options.directory, arcname=os.path.basename(options.directory))
        print "Done writing a tar file"

    # return the log file
    sys.stdout.close()
    sys.stdout = stdoutFd
    return log_file_name

def main(args):
    arg_obj = parse_args(args)
    return makeMapUIfiles(arg_obj, args)

def fromNodejs(args):
    return main(args)

if __name__ == "__main__" :
    try:
        return_code = main(sys.argv[1:])
    except:
        traceback.print_exc()
        return_code = 1

    sys.exit(return_code)
