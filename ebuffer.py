#-*- coding:utf-8 -*-

import sys, os
static_buffer1=""
static_buffer0 = "helloworld,this is a crazy world!\n"

S_OFFSET=0
S_LENGTH=1
S_BUFFER=2

# offset length buffer 
span_1=[0,len(static_buffer0),0]
chains=[ span_1 ]
# first  last  length boundry 
UNDO_FIRST=0
UNDO_LAST =1
UNDO_LENGTH=2
UNDO_BOUNDRY=3

undo_range=[(0,0,0,0),([],[])]
undo_stack=[]
redo_stack=[]
last_edit="init"
# from (0/-1 length+1] cur_index [0   xx)
def span_from_index( index ):
	cur_index = 0
	span_index = 0
	for span in chains:
		if index > cur_index and index <= (cur_index + span[S_LENGTH]):
			return (span,span_index,cur_index)
		cur_index += span[S_LENGTH]
		span_index +=1
	else:
		print index,"is beyond range"

def last_pos():
	cur = 0
	for span in chains:
		cur += span[S_LENGTH]
	return cur

def span_offset(sp):
	return sp[S_OFFSET]
def span_length(sp):
	return sp[S_LENGTH]
def span_buffer(sp):
	return sp[S_BUFFER]

def buffer1_add(strp):
	global static_buffer1
	static_buffer1 +=strp




def print_chains():
	for span in chains:
		if span[S_BUFFER] == 0:
			sys.stdout.write( static_buffer0[span[S_OFFSET]:span[S_OFFSET]+span[S_LENGTH]] )
		elif span[S_BUFFER] == 1:
			sys.stdout.write( static_buffer1[span[S_OFFSET]:span[S_OFFSET]+span[S_LENGTH]] )

def span_insert(index, length, stpr):
	global last_edit 
	_span = span_from_index(index) 
	if _span == None and index !=0 :
		print "out of range"
		return 
	
	print _span
	if index ==0 :
		chains.insert(0,[len(static_buffer1),length,1] )
		""" For undo-ops """
		_range=[(-1,0,0,1),([])]
		span_undo_push(_range)

		""" First Check Boundry """
	elif ( _span[2] + span_length(_span[0]) ) == index:

		if last_edit == "insert" and _span[2] + _span[0][S_LENGTH] == index:
			""" Just extend last insert """
			print "S 1 just append last piece"
	
			chains[_span[1]][S_LENGTH] += length
		else:
			print "boundry insert"

			chains.append([len(static_buffer1),length,1])
			_range = [(_span[1],_sapn[1]+1,0,1),([])]
			span_undo_push(_range)
	
	else:
		""" ordinary insert in middle of something """
		old_buffer = _span[0][S_BUFFER]
		spot_id = _span[1]
		""" Last is unused in vector for python, and not effective to define a fun of swap """
		span_undo_push( [ (spot_id,spot_id+2,1,0), (_span[0]) ] )

		chains[spot_id]=[_span[0][S_OFFSET] + index - _span[2], span_length(_span[0])-(index-_span[2]),old_buffer]
		chains.insert(spot_id,[len(static_buffer1), length, 1]) # _t
		chains.insert(spot_id,[_span[0][S_OFFSET], index-_span[2], old_buffer]) # _t1


	buffer1_add(stpr)  # update modify_buffer static_buffer1
	last_edit="insert" #
	span_status()

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
		old_buffer = _span_start[0][S_BUFFER]
		_t = [len(static_buffer1), length, 1]
		_t1= [span_offset(_span_start[0]), index-_span_start[2], old_buffer]
		_t2= [span_offset(_span_start[0]) + index - _span_start[2] + length,
		      span_length(_span_start[0])-(index-_span_start[2])- length, old_buffer]
		spot_id = _span_start[1]
		chains[spot_id] = _t2
		chains.insert(spot_id,_t)
		chains.insert(spot_id,_t1)

		span_undo_push([ (spot_id,spot_id+2,0,0) ,( _span_start[0] ) ])
	else:
		""" replace cross multi-spans """
		_t_first = [span_offset(_span_start[0]), index- _span_start[2], _span_start[0][S_BUFFER]]
		_t_last  = [span_offset(_span_end[0])+length + index - _span_end[2],
			    span_length(_span_end[0]) - (length + index - _span_end[2]), _span_end[0][S_BUFFER]]
		_t_replace = [len(static_buffer1), length, 1 ]

		span_undo_push([(_span_start[1],_span_start[1]+2,0,0 ), ( chains[_span_start[1]:_span_end[1]+1] )])			

		chains[_span_start[1]] = _t_first
		chains[_span_end[1]] = _t_last

		""" delete all cross-spans """
		i = _span_start[1] + 1
		while i<_span_end[1]:
			chains.pop(i)
			i += 1
		if _span_end[1] - _span_start[1] >0 :
			chains.insert(_span_start[1]+1,_t_replace)

	buffer1_add(pstr)
	last_edit="replace"
	span_status()


def span_erase(index, length):
	_span_start = span_from_index(index)
	_span_end   = span_from_index(index+length)
	
	""" For buff-char-on-screen index up from [1 length] """	
	index -=1 
	
	if _span_start[1] == _span_end[1]:
		""" only one span will be Deleted ,do NOT opt this"""
		old_buffer = _span_start[0][S_BUFFER]
		
		_t1= [span_offset(_span_start[0]), index-_span_start[2], old_buffer]
		_t2= [span_offset(_span_start[0]) + index - _span_start[2] + length,
		      span_length(_span_start[0])-(index-_span_start[2])- length, old_buffer]
		spot_id = _span_start[1]
		chains[spot_id] = _t2
		chains.insert(spot_id,_t1)
		span_undo_push([ (spot_id,spot_id+1,0,0) ,( _span_start[0] ) ])
	else:
		""" replace cross multi-spans """
		_t_first = [span_offset(_span_start[0]), index- _span_start[2], _span_start[0][S_BUFFER]]
		_t_last  = [span_offset(_span_end[0])+length + index - _span_end[2],
			    span_length(_span_end[0]) - (length + index - _span_end[2]), _span_end[0][S_BUFFER]]
		_t_replace = [len(static_buffer1), length, 1 ]

		span_undo_push([(_span_start[1],_span_start[1]+1,0,0 ), ( chains[_span_start[1]:_span_end[1]+1] )])				

		chains[_span_start[1]] = _t_first
		chains[_span_end[1]] = _t_last
		
		""" delete all cross-spans """
		i = _span_start[1] + 1
		while i<_span_end[1]:
			chains.pop(i)
			i += 1
	last_edit="erase"
	span_status()


def span_undo_push(var_sp):
	""" first last length boundry: last is unused  """
	undo_stack.append(var_sp)
def span_redo_push(var_sp):
	redo_stack.append(var_sp)
def span_stack_push(var_stack, var_sp):
	var_stack.append(var_sp)
def span_swap(var_stack,var_stack2,*arg):
	""" replace chains with var_stack[-1], then push it in var_stack2[-1] """
	if not var_stack:
		""" stack is empty """
		return
	_undop = var_stack.pop()
	_pos = _undop[0]
	_span  = _undop[1]
	if _undop == None:
		return

	""" if boundry is 1 """
	if _pos[UNDO_BOUNDRY] ==1:
		_redosp = chains.pop(_pos[UNDO_FIRST+1])
		span_stack_push(var_stack2, [(_pos[UNDO_FIRST+1],_pos[UNDO_FIRST],1,0),(_redosp) ])
	else:
		
		_firstid = _pos[UNDO_FIRST]
		_lastid  = _pos[UNDO_LAST] >=len(chains) and -1 or (_pos[UNDO_LAST])
		_l = len(chains)
		if _firstid>_l:
			return

		_redosp  = chains[ _firstid : _lastid+1 ] 
		
		span_stack_push(var_stack2, [(_firstid, _firstid+len(_span)-1 , 0, 0 ), (_redosp) ])
		if isinstance(_span[0],(list,tuple)):
			if _firstid == _l:
				chains.append(_span)
			else:
				chains[_firstid:_lastid+1] = _span
		else:
			if _firstid == _l:
				chains.append([_span])
			else:
				chains[_firstid:_lastid+1] = [_span]

	last_edit = "undo_redo"
	span_status(arg[0])
def span_undo():
	print "undo-stack:",undo_stack
	span_swap(undo_stack, redo_stack,'undo')
	print 'undo-stack:after:',undo_stack
def span_redo():
	span_swap(redo_stack, undo_stack,'redo')
	

def span_status(*pstr):
	print chains
	print static_buffer1
	print_chains()
	print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",pstr and pstr[0].upper() or ""

print "before orgi",chains
#print span_from_index(4)
print_chains()
print " "

#=[{"offset":0,S_LENGTH:2,"buffer":1}]
span_insert(5,2,", ")

span_insert(7,2,"__")
span_undo()
print_chains()
span_insert(0,3,"SKY")

span_insert(3,1,"W")


span_replace(1,12,"skysmilerbdf")
span_undo()

#span_erase(1,3)
span_undo()
print undo_stack
span_undo()
print "asdf"
span_redo()
span_redo()
