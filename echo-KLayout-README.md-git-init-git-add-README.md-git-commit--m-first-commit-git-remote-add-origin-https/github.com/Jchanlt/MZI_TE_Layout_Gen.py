########################################################################
#Author: Jeffrey Chan 	    				                 #
#Purpose: This script serves to generate a waveguide layout     	   #
#		  where the ratio of waveguide to heater is maximised.    #
#Credits to Jaspreet Jhoja for the basis of this code.                 #
#Acknowledgments: Jaspreet Jhoja                                       #
########################################################################

import pya





#Get current object handles

lv = pya.Application.instance().main_window().current_view()
if lv == None:
  raise Exception("No view selected")

# Find the currently selected layout.
ly = pya.Application.instance().main_window().current_view().active_cellview().layout() 
if ly == None:
  raise Exception("No layout")

# find the currently selected cell:
cell = pya.Application.instance().main_window().current_view().active_cellview().cell
if cell == None:
  raise Exception("No cell")

# fetch the database unit (nanometer)
dbu = 1 / ly.dbu


#space between the designs
space = 100

# clean all cells within "cell"
ly.prune_subcells(cell.cell_index(), -1)

# Layer mapping:
LayerSi = pya.LayerInfo(1, 0)
LayerSiN = cell.layout().layer(LayerSi)
LayerT = pya.LayerInfo(10, 0)
LayerTN = cell.layout().layer(LayerT)
LayerM = pya.LayerInfo(11, 0)
LayerMN = cell.layout().layer(LayerM)
fpLayer = pya.LayerInfo(99, 0)
fpLayerN = cell.layout().layer(fpLayer)
TextLayer = pya.LayerInfo(10, 0)
TextLayerN = cell.layout().layer(TextLayer)

# clean all cells within "cell"
ly.prune_subcells(cell.cell_index(), 10)

  # Grating couplers, P1orts 1, 2, 3, 4 (top-down):
GC_imported = ly.create_cell("ebeam_gc_te1550", "SiEPIC-EBeam").cell_index()
print ("Cell: GC_imported: #%s" % GC_imported)
 #Ybranch import and setup
branch_imported = ly.create_cell("ebeam_y_1550", "SiEPIC-EBeam").cell_index()

# Draw floor plan (Die limit)
cell.shapes(fpLayerN).insert(pya.Box(0,0, 1500*dbu, 1200*dbu))

def addp(path, direction, length): #function to concatenate next steps to draw a path
  if not path:
  	raise NameError('List is empty!')

  if direction not in ('up', 'down', 'left', 'right'):
  	raise NameError('Unknown Direction')

  last_index = len(path)-1
  last_point = path[last_index] 

  if direction == 'up':
    New_last_point = [last_point[0],last_point[1]+length]
  elif direction == 'down':
    New_last_point = [last_point[0],last_point[1]-length]
  elif direction == 'left':
  	New_last_point = [last_point[0]-length,last_point[1]]
  elif direction == 'right':
  	New_last_point = [last_point[0]+length,last_point[1]]
  
  path = path + [New_last_point]

  return path

def spiralp(path, entrance, guide_spacing, width, height, guide_width, end):
  if entrance not in ('top', 'bottom'):
    raise NameError('Unkonwn Entry point!')
  
  if entrance == 'bottom': #spiral in clockwise
    path = addp(path, 'left', width+guide_spacing*2+guide_width*2)
    path = addp(path, 'up', height)
    path = addp(path, 'right', width)
    path = addp(path, 'down', height-(guide_spacing*2+guide_width*2))

    if height-(guide_spacing*2+guide_width) <= (b_radi*2+guide_spacing*2 + guide_width) or width <= (b_radi*4+guide_spacing+guide_width):
      if end == 'yes':
        path = addp(path, 'left', (width-guide_spacing-guide_width)/2)
        path = addp(path, 'up', (height-guide_spacing*2-b_radi+guide_width))
        path = addp(path, 'left', (width-guide_spacing-guide_width)/2)
        path = addp(path, 'down', (height-guide_spacing-b_radi+guide_width*2))
        path = addp(path, 'right', b_radi+guide_spacing*2-guide_width*2)
    else:
      return spiralp(path, entrance, guide_spacing, (width-guide_spacing*2*2-guide_width*2*2), (height-guide_spacing*2*2-guide_width*2*2), guide_width, end)
  return path

 
for i in range(0, 300, 85):

  gc_x_start = 1470
  gc_y_start = 20
  gc_y_space = 127
  wg_width = 0.5
  b_radi = 5 #bend radius
  t = pya.Trans(pya.Trans.R0, (gc_x_start-i)*dbu, (gc_y_start+(i/2))*dbu) #Set gc array starting point
  y = pya.Trans(pya.Trans.R0, (gc_x_start+7.4-i)*dbu, (gc_y_start+(i/2)+gc_y_space)*dbu)#Set input y branch array starting point
  y2 = pya.Trans(pya.Trans.R270, (gc_x_start+14.8+5-i)*dbu, (gc_y_start+(i/2)+254-7.4-5)*dbu)#Set output y branch array starting point
  y3 = pya.Trans(pya.Trans.R90, (gc_x_start+14.8+5-i)*dbu, (gc_y_start+(i/2)+gc_y_space+7.4+5+2.75)*dbu)#Split Interferometer path here
  #Placing components
  cell.insert(pya.CellInstArray(GC_imported, t, pya.Point(0,gc_y_space*dbu), pya.Point(0,0), 9, 1)) #Places Grating Couplers on the right
  cell.insert(pya.CellInstArray(branch_imported, y, pya.Point(0,3*gc_y_space*dbu), pya.Point(0,0), 3, 1)) #Placing input Y branch (splitting)
  for index in range(0, 3, 1):
    label_t = pya.Trans((gc_x_start-i)*dbu, (gc_y_start+(i/2)+gc_y_space+gc_y_space*3*(index))*dbu) #Set automated testing label array starting point
    cell.shapes(LayerTN).insert(pya.Text(("opt_in_TE_1550_ELEC463_JeffreyC_MZI%d-%d" %(index+1, (i/85)+1)), label_t))
  cell.insert(pya.CellInstArray(branch_imported, y2, pya.Point(0,3*gc_y_space*dbu), pya.Point(0,0), 3, 1)) #Placing output Y branches (recombine)
  cell.insert(pya.CellInstArray(branch_imported, y3, pya.Point(0,3*gc_y_space*dbu), pya.Point(0,0), 3, 1)) #placing y branch to split interferometer
  #Placing waveguides

  #Placing output waveguides
  pout_x = (gc_x_start-i)
  pout_y = (gc_y_start+(i/2)+(gc_y_space*2))
  p = pya.Trans(pya.Trans.R0, pout_x*dbu, pout_y*dbu) #Set MZI recombined wavegout to output

  points_L1 = [ [pout_x, pout_y], [pout_x+5+14.8, pout_y], [pout_x+5+14.8, pout_y-5] ] 
  layout_waveguide_abs(cell, LayerSi, points_L1, wg_width, b_radi)
  cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH"), p, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))
  
  #placing path to MZI splitter 
  p2out_x = pout_x+14.8	
  p2out_y = pout_y-gc_y_space+2.75
  p2 = pya.Trans(pya.Trans.R0, p2out_x*dbu, p2out_y*dbu) #Set MZI recombined wavegout to output

  points_L2 = [ [p2out_x, p2out_y], [p2out_x+5, p2out_y], [p2out_x+5, p2out_y+5] ]
  layout_waveguide_abs(cell, LayerSi, points_L2, wg_width, b_radi)
  cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$1"), p2, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))
  
  #placing mzi cold path
  pmzic_x = p2out_x+5+2.75
  pmzic_y = p2out_y+5+14.8
  p3 = pya.Trans(pya.Trans.R0, pmzic_x*dbu, pmzic_y*dbu) #Set MZI cold path origin (begins near input gc)

  points_mzic = [ [pmzic_x, pmzic_y], [pmzic_x, pmzic_y+gc_y_space-5-5-14.8-14.8-2.75]]
  layout_waveguide_abs(cell, LayerSi, points_mzic, wg_width, b_radi)
  cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$2"), p3, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))

  #placing gc benchmark path to output 2
  pgcb_x = p2out_x
  pgcb_y = p2out_y-5.5
  p4 = pya.Trans(pya.Trans.R0, pgcb_x*dbu, pgcb_y*dbu) #Set origin of gc benchmark path to output2 

  points_pgcb = [ [pgcb_x, pgcb_y], [pgcb_x+5, pgcb_y], [pgcb_x+5, pgcb_y-gc_y_space+2.75], [pgcb_x+5-5-14.8, pgcb_y-gc_y_space+2.75]]
  layout_waveguide_abs(cell, LayerSi, points_pgcb, wg_width, b_radi)
  cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$3"), p4, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))

  #placing the heated path
  pmzih_x = pmzic_x-5.5
  pmzih_y = pmzic_y
  p5 = pya.Trans(pya.Trans.R0, pmzih_x*dbu, pmzih_y*dbu) #Set MZI hot path origin (begins near input gc)
  p6 = pya.Trans(pya.Trans.R0, pmzih_x*dbu, (pmzih_y+gc_y_space-5-5-14.8-14.8-2.75)*dbu) #Set MZI hot return path origin (begins near output gc)

  #Creating the sprial path (this is where the fun begins)
  wg_spacing = 3
  #First route the gc structures into the correct designated areas 
  spiral_height = 381-24.5
  spiral_width = 106
  route = [[pmzih_x,pmzih_y]]
  route = addp(route, 'up', 5)
  route = addp(route, 'left', 60)
  route = addp(route, 'down', 138+(i/2)-wg_width*(2+i/85*2)-wg_spacing*(2+i/85*2))
  route = addp(route, 'left', 500-(i/85)*(wg_width*2+wg_spacing*2)-i)
  route = addp(route, 'up', spiral_height-(wg_spacing+wg_width)) #+(i/85)*(wg_width+wg_spacing)
  route = addp(route, 'left', b_radi*2+i*2.8)
  route = addp(route, 'down', spiral_height-(wg_spacing+wg_width)+(i/85)*(wg_width*2*2+b_radi)) #+(i/85)*(wg_width+wg_spacing)

  #create route back
  route_b = [[pmzih_x, pmzih_y+gc_y_space-5-5-14.8-14.8-2.75]]
  route_b = addp(route_b, 'down', 5)
  route_b = addp(route_b, 'left', 60+wg_spacing)
  route_b = addp(route_b, 'down', 138-wg_spacing+(gc_y_space-b_radi*2-14.8-14.8-2.75)-b_radi*2-wg_width+(i/2)-wg_width*(2+i/85*2)-wg_spacing*(2+i/85*2))
  route_b = addp(route_b, 'left', 500-wg_width-wg_spacing*2-(i/85)*(wg_width*2+wg_spacing*2)-i)
  route_b = addp(route_b, 'up', spiral_height-(wg_spacing+wg_width)) #+(i/85)*(wg_width+wg_spacing)
  route_b = addp(route_b, 'left', b_radi*2+i*2.8+wg_spacing*2+wg_width*2)
  route_b = addp(route_b, 'down', spiral_height-(wg_spacing+wg_width)+(i/85)*(wg_width*2*2+b_radi)) #+(i/85)*(wg_width+wg_spacing)
  #Then start the spiral
  route = spiralp(route, 'bottom', wg_spacing, spiral_width, spiral_height, 0.5, 'no') #make one side of the spiral
  route_b = spiralp(route_b, 'bottom', wg_spacing, spiral_width-wg_spacing*2-wg_width*2, spiral_height-wg_spacing*2-wg_width*2, 0.5, 'yes')#make the other side
  route_b = addp(route_b, 'left', b_radi) #This is a very curious step. it turns out that the path to waveguide script doesn't like loops, had to make two waveguides then join the together.
  route = route + list(reversed(route_b)) #concatenating the two routes  

 
  if i == 0:
    layout_waveguide_abs(cell, LayerSi, route, wg_width, b_radi)
    cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$4"), p5, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))

  elif i == 85:
    layout_waveguide_abs(cell, LayerSi, route, wg_width, b_radi)
    cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$5"), p5, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))
 
  elif i == 85*2:
    layout_waveguide_abs(cell, LayerSi, route, wg_width, b_radi)
    cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$6"), p5, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))
   
  elif i == 85*3:
    layout_waveguide_abs(cell, LayerSi, route, wg_width, b_radi)
    cell.insert(pya.CellInstArray(ly.cell_by_name("ROUND_PATH$7"), p5, pya.Point(0,3*gc_y_space*dbu),pya.Point(0,0), 3, 1))
  else: 
   	raise Exception('Did you change the i increment? please change from 85 to your desired wavelength near the end of the spiral code.')
  
  #rAdding metal heater parts
  for j in range (0, 3, 1):
    m_width = 10
    box_array_start = [5*dbu+(i/85)*231*dbu, 43*dbu+j*381*dbu] #Placing Metal Pads 
    pad_size = 100*dbu
    cell.shapes(LayerMN).insert(pya.Box(
    box_array_start[0],
    box_array_start[1], 
    box_array_start[0]+pad_size, 
    box_array_start[1]+pad_size)) 

    cell.shapes(LayerMN).insert(pya.Box(
    box_array_start[0],
    box_array_start[1]+(spiral_height*dbu)-pad_size, 
    box_array_start[0]+pad_size, 
    box_array_start[1]+(spiral_height*dbu))) 

    # #Placing paths
    # m_route = [[box_array_start[0]+pad_size*dbu, box_array_start[1]+m_width/2*dbu]]
    # m_route = addp(m_route, 'right', 100)
    # m_route = addp(m_route, 'up', 345)
    

    # layout_waveguide_abs(cell, LayerSi, m_route, m_width, b_radi)


  
