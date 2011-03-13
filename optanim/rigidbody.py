from __future__ import division
import sympy
from constraint import *
from utils import *

class RigidBody(object):
    '''Represents a rigid body.'''

    def __init__(self, Name, Mass, Diameter):
	'''Constructor'''
	
	#unpack diameters as radii for convienience
	a,b,c = [x/2.0 for x in Diameter]

	self.Name = Name

	#mass vector (diagonals of a mass matrix) for a solid ellipsoid
	self.Mass = [Mass, Mass, Mass,	#translational
	    (Mass / 5.0) * (b**2+c**2),	#rotational
	    (Mass / 5.0) * (a**2+c**2),
	    (Mass / 5.0) * (a**2+b**2)]

	self.Diameter = Diameter
	self.q = [
	    sympy.Symbol(Name + "_qtx"), #translational
	    sympy.Symbol(Name + "_qty"),
	    sympy.Symbol(Name + "_qtz"),

	    sympy.Symbol(Name + "_qrx"), #rotational
	    sympy.Symbol(Name + "_qry"),
	    sympy.Symbol(Name + "_qrz")]

	#these references make it convenient to traverse the character as a tree
	self.ChildList = []
	self.Parent = None
	self.ChildJointList = []
	self.ParentJoint = None

	print 'new ' + str(self)

    def __str__(self):
	return 'RigidBody "' + self.Name + '": diameter = ' + str(self.Diameter) + ', mass = ' + str(self.Mass)
    
    def add_child(self, body):
	self.ChildList.append(body)

    def set_parent(self, body):
	if(self.Parent is not None):
	    raise BaseException(self.Name + " already has parent body assigned! Make sure you're creating joints such that BodyA always points 'up' towards Root.")
	self.Parent = body

    def add_child_joint(self, joint):
	self.ChildJointList.append(joint)

    def set_parent_joint(self, joint):
	if(self.ParentJoint is not None):
	    raise BaseException(self.Name + " already has parent joint assigned! Make sure you're creating joints such that BodyA always points 'up' towards Root.")
	self.ParentJoint = joint

    def ep_a(self):
	'''returns the position of endpoint A in body local coordinates'''
	return [0.0, self.Diameter[1] / 2.0, 0.0]

    def ep_b(self):
	'''returns the position of endpoint B in body local coordinates'''
	return [0.0, -self.Diameter[1] / 2.0, 0.0]

    def get_intersection_constraint(self, worldpoint):
	#unpack diameters as radii for convienience
	a,b,c = [x/2.0 for x in self.Diameter]
	#transform point into body-local coordinates
	x,y,z = world_xf(worldpoint, [bq(t) for bq in self.q], worldToLocal=True)
	return Constraint('NoIntersection_' + self.Name, 1, (x**2/a**2) + (y**2/b**2) + (z**2/c**2))