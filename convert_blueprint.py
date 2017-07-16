#python!!!

import sys
import os
import xml.etree.ElementTree as XML

if len(sys.argv) < 2:
  quit()

#read in offsets file
OFFSET_FILE= str(os.path.dirname(os.path.realpath(sys.argv[0]))) + "\\block_offsets.xml"
print( OFFSET_FILE )
block_offsets = dict()
tree = XML.parse( OFFSET_FILE )
blocks = tree.getroot()
if blocks is not None:
  for block in blocks.findall('block'):
    subtype = block.attrib['subtype']
    if subtype is not None:
      block_offsets[subtype] = dict()
      for offset in block.findall('offset'):
        orientation=(offset.attrib['Forward'], offset.attrib['Up'])
        block_offsets[subtype][orientation] = dict()
        for index in ['x', 'y', 'z']:
          if index in offset.attrib:
            block_offsets[subtype][orientation][index] = int(offset.attrib[index])
          else:
            block_offsets[subtype][orientation][index] = int(0)

#print(block_offsets)

#convert blueprint
args = iter(sys.argv)
next(args)
for file in args:
  try:
    tree = XML.parse( file )
  except:
    continue

  root = tree.getroot()
  root.attrib['xmlns:xsd']="http://www.w3.org/2001/XMLSchema"
  cubegrids = None
  name = None
  if root.tag != "Definitions":
    continue

  #either a blueprint or a prefab
  if root.find("ShipBlueprints") is not None:
    cubegrids = root.find("ShipBlueprints").find("ShipBlueprint").find("CubeGrids")
  else:
    cubegrids = cubegrids = root.find("Prefabs").find("Prefab").find("CubeGrids")
  #if there are any cubegrids defined
  if cubegrids is not None:
    for cubegrid in cubegrids.findall('CubeGrid'):
      gridsize = cubegrid.find('GridSizeEnum')
      if(gridsize is not None and gridsize.text == 'Large'):
        print('... supersizing ' + file)
        gridsize.text = 'Small'
        cubeblocks = cubegrid.find('CubeBlocks')
        if cubeblocks is not None:
          for block in cubeblocks.findall('MyObjectBuilder_CubeBlock'):
            min = None
            if block.find('Min') is None:
              block.append(XML.Element('Min'))
              min = block.find('Min')
              min.set('x','0')
              min.set('y','0')
              min.set('z','0')
              min.tail = "\n            "
              #block.find('EntityId').tail="\n              "
            else:
              min = block.find('Min')
            ## default orientation to 'Forward' / 'Up'
            orientation=("Forward","Up")
            if block.find('BlockOrientation') is not None:
              orientation = (block.find('BlockOrientation').attrib['Forward'], block.find('BlockOrientation').attrib['Up'])
            ## adjust the offsets
            for index in ['x', 'y', 'z']:
              if index in min.attrib:
                min.attrib[index] = str(int(min.attrib[index])*5)
              if block.find('SubtypeName') is not None:
                subtype = block.find('SubtypeName').text
                if subtype in block_offsets and orientation in block_offsets[subtype]:
                  min.attrib[index] = str(int(min.attrib[index]) + block_offsets[subtype][orientation][index])
  tree.write(file,
             xml_declaration = True,
             encoding = 'utf-8',
             method = 'xml',
            )