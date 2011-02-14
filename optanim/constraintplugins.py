from constraint import *
from utils import *

class ConstraintPlugin(object):
    '''Base class for constraint plugins'''
    def __init__(self):
	pass

    def get_constraints(self, character): abstract
    '''Returns a list of constraints generated by the plugin'''


class ConstraintPluginLoop(ConstraintPlugin):
    '''A constraint plugin that enforces cyclic (looping) motion'''

    def __init__(self, offset=[0, 0, 0]):
	'''Constructor'''
	self.offset = offset
	ConstraintPlugin.__init__(self)

    def get_constraints(self, character):
	retList = []

	#first frame connects to last
	retList.extend(character.get_newtonian_constraints(
		       'LoopBegin', 'pTimeEnd', 'pTimeBegin', 'pTimeBegin+1', 't=pTimeBegin', [-n for n in self.offset]))

	#last frame connects to first
	retList.extend(character.get_newtonian_constraints(
		       'LoopEnd', 'pTimeEnd-1', 'pTimeEnd', 'pTimeBegin', 't=pTimeEnd', self.offset))

	return retList


class ConstraintPluginGroundPlane(ConstraintPlugin):
    '''A constraint plugin that keeps bodies on or above the ground plane'''

    def __init__(self):
	'''Constructor'''
	ConstraintPlugin.__init__(self)

    def get_constraints(self, character):
	retList = []
	for body in character.bodyList:
	    worldpointA = world_xf(body.ep_a(), [bq(t) for bq in body.q])
	    worldpointB = world_xf(body.ep_b(), [bq(t) for bq in body.q])
	    retList.append(Constraint(body.Name + '_AboveGroundPlane_A', lb=0, c=worldpointA[1]))
	    retList.append(Constraint(body.Name + '_AboveGroundPlane_B', lb=0, c=worldpointB[1]))
	return retList