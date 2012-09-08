"""
COLLECTION OF SUPPORTING FUNCTIONS AND CLASSES
"""
from copy import deepcopy
from ..solvers.steadystate import ManualSteadyState
from pymaclab.dsge.helpers import deep_eq

queue = []

class Updaters_Queued(object):
    def __init__(self):
        pass

class dicwrap_queued:
    def __init__(self,other,wrapobj_str,initlev):
        self.other = other
        self.queue = other.updaters_queued.queue
        self.wrapobj_str = wrapobj_str
        self.initlev = initlev
        if wrapobj_str == 'self.vardic':
            self.wrapdic = deepcopy(other.vardic)
        elif wrapobj_str == 'self.nlsubsdic':
            self.wrapdic = deepcopy(other.nlsubsdic)
        elif wrapobj_str == 'self.paramdic':
            self.wrapdic = deepcopy(other.paramdic)
            
    def __getattr__(self,attrname):
        return getattr(self.wrapdic,attrname)

    def __setitem__(self,key,value):
        other = self.other
        initlev = self.initlev
        wrapobj_str = self.wrapobj_str
        # Create the wrapobj using the passed string
        wrapobj = eval('other.'+wrapobj_str.split('.')[1])
        # ...and assign before test of inequality
        wrapobj[key] = value
        if self.wrapdic != wrapobj:
            self.wrapdic[key] = value
            if wrapobj_str == 'self.nlsubsdic':
                for i1,elem in enumerate(other.nlsubs_raw1):
                    other.nlsubs_raw1[i1][1] = deepcopy(self.nlsubsdic[other.nlsubs_raw1[i1][0]])
                self.queue.append('self.nlsubsdic')
            elif wrapobj_str == 'self.paramdic':
                self.queue.append('self.paramdic')
            elif wrapobj_str == 'self.vardic':
                self.queue.append('self.vardic')           

    def __getitem__(self,key):
        return self.wrapdic[key]

    def update(self,dico):
        self.updic = dico
        other = self.other
        initlev = self.initlev
        wrapobj_str = self.wrapobj_str
        # Create the wrapobj using the passed string
        wrapobj = eval('other.'+wrapobj_str.split('.')[1])
        # ...and update befor test of inequality
        wrapobj.update(dico)
        # Check if new keys are already present in wrapdic
        for keyo in dico.keys():
            if keyo not in self.wrapdic.keys():
                print "ERROR: You can only update existing keys, not introduce new ones."
                return
        # Check if any key's value has been updated relative to wrapdic
        if self.wrapdic != wrapobj:
            self.wrapdic.update(dico)
            if wrapobj_str == 'self.nlsubsdic':
                for i1,elem in enumerate(other.nlsubs_raw1):
                    other.nlsubs_raw1[i1][1] = deepcopy(self.nlsubsdic[other.nlsubs_raw1[i1][0]])
                self.queue.append('self.nlsubsdic')
            elif wrapobj_str == 'self.paramdic':
                self.queue.append('self.paramdic')
            elif wrapobj_str == 'self.vardic':
                self.queue.append('self.vardic')           


    def __repr__(self):
        return self.wrapdic.__repr__()
    def __str__(self):
        return self.wrapdic.__str__()


class listwrap_queued:
    def __init__(self,other,wrapobj_str,initlev):
        self.other = other
        self.queue = other.updaters_queued.queue
        self.wrapobj_str = wrapobj_str
        self.initlev = initlev
        if wrapobj_str == 'self.foceqs':
            self.wrapli = deepcopy(other.foceqs)

    def __setslice__(self,ind1,ind2,into):
        other = self.other
        wrapob_str = self.wrapobj_str
        initlev = self.initlev
        lengo = len(self.wrapli)
        if ind2 >= lengo:
            print "ERROR: Assignment out of bounds of original list"
            return

        if self.wrapli[ind1:ind2] != into and wrapob_str == 'self.foceqs':
            self.wrapli[ind1:ind2] = into
            other.foceqs[ind1:ind2] = into
            self.queue.append('self.foceqs')
    
    def __setitem__(self,ind,into):
        other = self.other
        wrapob_str = self.wrapobj_str
        initlev = self.initlev
        lengo = len(self.wrapli)
        if ind >= lengo:
            print "ERROR: Assignment out of bounds of original list"
            return

        if self.wrapli[ind] != into and wrapob_str == 'self.foceqs':
            self.wrapli[ind] = into
            other.foceqs[ind] = into
            self.queue.append('self.foceqs')

    def __getitem__(self,ind):
        lengo = len(self.wrapli)
        if ind >= lengo:
            print "ERROR: Assignment out of bounds of original list"
            return
        else:
            return self.wrapli[ind]

    def __repr__(self):
        return self.wrapli.__repr__()
    def __str__(self):
        return self.wrapli.__str__()


class matwrap_queued:
    def __init__(self,other,wrapobj_str,initlev):
        self.other = other
        self.queue = other.updaters_queued.queue
        self.wrapobj_str = wrapobj_str
        self.initlev = initlev
        if wrapobj_str == 'self.sigma':
            self.wrapmat = deepcopy(other.sigma)
            
    def __getattr__(self,attrname):
        return getattr(self.wrapmat,attrname)
    
    def __setitem__(self,ind,into):
        # ind is a tuple and into is (should be) a float
        other = self.other
        wrapob_str = self.wrapobj_str
        initlev = self.initlev
        if type(into) != type(1.111): into = float(into)
        if self.wrapmat[ind[0],ind[1]] != into and wrapob_str == 'self.sigma':
            self.wrapmat[ind[0],ind[1]] = into
            other.sigma[ind[0],ind[1]] = into
            self.queue.append('self.sigma')

   
class Process_Queue(object):
    def __init__(self,other=None):
        self.other = other
        self.queue = other.updaters_queued.queue
        self.initlev = other._initlev
        # The vardic
        self.vardic = other.updaters_queued.vardic
        # The nlsubsdic
        self.nlsubsdic = other.updaters_queued.nlsubsdic
        # The paramdic
        self.paramdic = other.updaters_queued.paramdic
        # The foceqs
        self.foceqs = other.updaters_queued.foceqs
        # The sigma
        self.sigma = other.updaters_queued.sigma
        
    def __call__(self):
        queue = self.queue
        other = self.other
        initlev = self.initlev
        ##### THE INITS #####################
        other.init1()
        if 'self.vardic' in queue:
            other.vardic = deepcopy(self.vardic)

        other.init1a()
        if 'self.nlsubsdic' in queue:
            for i1,elem in enumerate(other.nlsubs_raw1):
                other.nlsubs_raw1[i1][1] = deepcopy(self.nlsubsdic[other.nlsubs_raw1[i1][0]])
            other.nlsubsdic = deepcopy(self.nlsubsdic)

        other.init1b()
        if 'self.paramdic' in queue:
            other.paramdic = deepcopy(self.paramdic)
        
        other.init1c()
        if 'self.foceqs' in queue:
            other.foceqs = deepcopy(self.foceqs)       

        # Prepare DSGE model instance for manual SS computation
        other.init2()
        if initlev == 0:
            other.init_out()

        # Solve for SS automatically
        other.init3()
        if initlev == 1:
            other.init_out() 

        other.init4()
        if 'self.sigma' in queue:
            other.sigma = deepcopy(self.sigma)

        # Solve model dynamically            
        other.init5()
        if initlev == 2:
            other.init_out()
            
        return
