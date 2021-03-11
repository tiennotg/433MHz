'''
  Copyright 2021 Guilhem Tiennot
  
  Implements a digital Schmitt trigger (see: https://en.wikipedia.org/wiki/Schmitt_trigger)
  
  This file is part of nexus_device.py.
  
  nexus_device.py is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  nexus_device.py is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with nexus_device.py.  If not, see <https://www.gnu.org/licenses/>.
'''

class SchmittTrigger():
    def __init__(self, thres1, thres2, initial_state=False):
        self._t1, self._t2, self._state, self._initial = thres1, thres2, initial_state, initial_state

    def compare(self, value):
        if self._state:
            if value < self._t1:
                self._state = False
        else:
            if value > self._t2:
                self._state = True
        return self._state

    def reset(self):
        self._state = self._initial
