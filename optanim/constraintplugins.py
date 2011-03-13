from constraint import *
from utils import *

class ConstraintPlugin(object):
    '''Abstract base class for constraint plugins. Constraint plugins provide a
    way to specify constraints that will perform the same function for any
    character, regardless of particular morphologies'''

    def __init__(self):
	pass

    def get_constraints(self, animation, character): abstract
    '''Returns a list of constraints generated by the plugin'''


class ConstraintPluginLoop(ConstraintPlugin):
    '''A constraint plugin that enforces cyclic (looping) motion'''

    def __init__(self, offset=[0]*dof):
	'''Constructor'''
	self.offset = offset
	ConstraintPlugin.__init__(self)

    def get_constraints(self, animation, character):
	retList = []

	#first frame connects to last
	retList.extend(character.get_newtonian_constraints(
	    'LoopBegin', 'pTimeEnd', 'pTimeBegin', 'pTimeBegin+1', 't=pTimeBegin', [-n*animation.Length for n in self.offset]))

	#last frame connects to first
	retList.extend(character.get_newtonian_constraints(
	    'LoopEnd', 'pTimeEnd-1', 'pTimeEnd', 'pTimeBegin', 't=pTimeEnd', [n*animation.Length for n in self.offset]))

	#TODO: HACK: we also have to loop the contact joint 'zero velocity' constraints, so here goes!
	for j in character.get_joints_contact():
	    tRangeOn = 't in sTimeSteps_' + j.Name + 'On'
	    worldpoint_t0 = world_xf(j.Point, [bq('pTimeBegin') for bq in j.Body.q])
	    worldpoint_t1 = world_xf(j.Point, [bq('pTimeEnd') for bq in j.Body.q])
	    retList.append(ConstraintEq(j.Name + '_state_x_loop', worldpoint_t0[0], worldpoint_t1[0] - self.offset[0]*animation.Length, TimeRange=tRangeOn + ' && t=pTimeBegin'))
	    retList.append(ConstraintEq(j.Name + '_state_z_loop', worldpoint_t0[2], worldpoint_t1[2] - self.offset[2]*animation.Length, TimeRange=tRangeOn + ' && t=pTimeBegin'))

	return retList


class ConstraintPluginGroundPlane(ConstraintPlugin):
    '''A constraint plugin that keeps bodies on or above the ground plane'''

    def __init__(self):
	'''Constructor'''
	ConstraintPlugin.__init__(self)

    def get_constraints(self, animation, character):
	retList = []
	for body in character.BodyList:
	    worldpointA = world_xf(body.ep_a(), [bq(t) for bq in body.q])
	    worldpointB = world_xf(body.ep_b(), [bq(t) for bq in body.q])
	    retList.append(Constraint(body.Name + '_AboveGroundPlane_A', lb=0, c=worldpointA[1]))
	    retList.append(Constraint(body.Name + '_AboveGroundPlane_B', lb=0, c=worldpointB[1]))
	return retList