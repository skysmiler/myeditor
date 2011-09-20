#-*- coding:utf-8 -*-

import sys, os
static_buffer1=""
static_buffer0 = "helloworld,this is a crazy world!\n"

# offset length buffer 
span_1={"offset":0,"length":len(static_buffer0),"buffer":0}
chains=[ span_1 ]

undo_range={"first":0,"last":0,"length":0,"boundry":0}
undo_stack=[]
last_edit="init"

# from (0/-1 length+1] cur_index [0   xx)
def span_from_index( index ):
	cur_index = 0
	span_index = 0
	for span in chains:
		if index > cur_index and index <= (cur_index + span["length"]):
			return (span,span_index,cur_index)
		cur_index += span["length"]
		span_index +=1
	else:
		print index,"is beyond range"

def last_pos():
	cur = 0
	for span in chains:
		cur += span["length"]
	return cur

def span_offset(sp):
	return sp["offset"]
def span_length(sp):
	return sp["length"]
def span_buffer(sp):
	return sp["buffer"]

def buffer1_add(strp):
	global static_buffer1
	static_buffer1 +=strp


def print_chains():
	for span in chains:
		if span["buffer"] == 0:
			sys.stdout.write( static_buffer0[span["offset"]:span["offset"]+span["length"]])
		elif span["buffer"] == 1:
			sys.stdout.write( static_buffer1[span["offset"]:span["offset"]+span["length"]] )


def span_insert(index, length, stpr):
	global last_edit 
	_span = span_from_index(index) 
	if _span == None and index !=0 :
		print "out of range"
		return 
	
	print _span
	if index ==0 :
		chains.insert(0,{"offset":len(static_buffer1),"length":length, "buffer":1})

		""" First Check Boundry """
	elif ( _span[2] + span_length(_span[0]) ) == index:

		if last_edit == "insert" and _span[2] + _span[0]["length"] == index:
			""" Just extend last insert """
			print "S 1 just append last piece"
	
			chains[_span[1]]["length"] += length
		else:
			print "boundry insert"

			chains.append({"offset":len(static_buffer1),"length":length,"buffer":1})
	
	
	else:
		""" ordinary insert in middle of something """
		old_buffer = _span[0]["buffer"]
		spot_id = _span[1]

		chains[spot_id]={"offset":span_offset(_span[0]) + index - _span[2], "length":span_length(_span[0])-(index-_span[2]),"buffer":old_buffer}
		chains.insert(spot_id,{"offset":len(static_buffer1), "length":length, "buffer":1}) # _t
		chains.insert(spot_id,{"offset":_span[0]["offset"], "length":index-_span[2], "buffer":old_buffer}) # _t1


	buffer1_add(stpr)  # update modify_buffer static_buffer1
	last_edit="insert" #
	print chains
	print static_buffer1

def span_replace(index, length, pstr):
	_span_start = span_from_index(index)
	_span_end   = span_from_index(index+length)
	
	""" check """
	if _span_start == None or _span_end == None:
		return

	""" For buff-char-on-screen index up from [1 length] """	
	index -=1 
	

	if _span_start[1] == _span_end[1]:
		""" only one span will be replaced ,do NOT opt this"""
		old_buffer = _span_start[0]["buffer"]
		_t = {"offset":len(static_buffer1), "length":length, "buffer":1}
		_t1= {"offset":span_offset(_span_start[0]), "length":index-_span_start[2], "buffer":old_buffer}
		_t2= {"offset":span_offset(_span_start[0]) + index - _span_start[2] + length,
		      "length":span_length(_span_start[0])-(index-_span_start[2])- length, "buffer":old_buffer}
		spot_id = _span_start[1]
		chains[spot_id] = _t2
		chains.insert(spot_id,_t)
		chains.insert(spot_id,_t1)
	else:
		""" replace cross multi-spans """
		_t_first = {"offset":span_offset(_span_start[0]), "length":index- _span_start[2], "buffer":_span_start[0]["buffer"]}
		_t_last  = {"offset":span_offset(_span_end[0])+length + index - _span_end[2],
			    "length":span_length(_span_end[0]) - (length + index - _span_end[2]), "buffer":_span_end[0]["buffer"]}
		_t_replace = {"offset":len(static_buffer1), "length":length, "buffer":1 }
	
		chains[_span_start[1]] = _t_first
		chains[_span_end[1]] = _t_last
		
		""" delete all cross-spans """
		i = _span_start[1] + 1
		while i<_span_end[1]:
			chains.pop(i)
			i += 1
		if _span_end[1] - _span_start[1] >1 :
			chains.insert(_span_start[1]+1,_t_replace)

	buffer1_add(pstr)
	last_edit="replace"
	
	print chains
	print static_buffer1

def span_erase(index, length):
	_span_start = span_from_index(index)
	_span_end   = span_from_index(index+length)
	
	""" For buff-char-on-screen index up from [1 length] """	
	index -=1 
	

	if _span_start[1] == _span_end[1]:
		""" only one span will be Deleted ,do NOT opt this"""
		old_buffer = _span_start[0]["buffer"]
		
		_t1= {"offset":span_offset(_span_start[0]), "length":index-_span_start[2], "buffer":old_buffer}
		_t2= {"offset":span_offset(_span_start[0]) + index - _span_start[2] + length,
		      "length":span_length(_span_start[0])-(index-_span_start[2])- length, "buffer":old_buffer}
		spot_id = _span_start[1]
		chains[spot_id] = _t2
		chains.insert(spot_id,_t1)
	else:
		""" replace cross multi-spans """
		_t_first = {"offset":span_offset(_span_start[0]), "length":index- _span_start[2], "buffer":_span_start[0]["buffer"]}
		_t_last  = {"offset":span_offset(_span_end[0])+length + index - _span_end[2],
			    "length":span_length(_span_end[0]) - (length + index - _span_end[2]), "buffer":_span_end[0]["buffer"]}
		_t_replace = {"offset":len(static_buffer1), "length":length, "buffer":1 }
	
		chains[_span_start[1]] = _t_first
		chains[_span_end[1]] = _t_last
		
		""" delete all cross-spans """
		i = _span_start[1] + 1
		while i<_span_end[1]:
			chains.pop(i)
			i += 1
		

def span_undo():
	pass
def span_redo():
	pass



print "before orgi",chains
#print span_from_index(4)
print_chains()
print " "

#=[{"offset":0,"length":2,"buffer":1}]
span_insert(5,2,", ")
print_chains()
span_insert(7,2,"__")
print_chains()
span_insert(0,3,"SKY")
print_chains()
print "<<<<<<<<<<<<<<<<<"
span_insert(3,1,"W")
print_chains()
print "<<<<<<<<<<<<<<<<<<<<<"
span_replace(1,12,"skysmilerbdf")
print_chains()
span_erase(1,3)
print_chains()
