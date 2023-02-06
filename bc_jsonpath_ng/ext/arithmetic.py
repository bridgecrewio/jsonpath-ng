#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import operator

from .. import DatumInContext, JSONPath

OPERATOR_MAP = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


class Operation(JSONPath):
    def __init__(self, left, op, right):
        self.left = left
        self.op = OPERATOR_MAP[op]
        self.right = right

    def find(self, datum):
        result = []
        if isinstance(self.left, JSONPath) and isinstance(self.right, JSONPath):
            left_results = self.left.find(datum)
            right_results = self.right.find(datum)
            if left_results and right_results and len(left_results) == len(right_results):
                for left, right in zip(left_results, right_results):
                    try:
                        result.append(self.op(left.value, right.value))
                    except TypeError:
                        return []
            else:
                return []
        elif isinstance(self.left, JSONPath):
            left_results = self.left.find(datum)
            for left in left_results:
                try:
                    result.append(self.op(left.value, self.right))
                except TypeError:
                    return []
        elif isinstance(self.right, JSONPath):
            right_results = self.right.find(datum)
            for right in right_results:
                try:
                    result.append(self.op(self.left, right.value))
                except TypeError:
                    return []
        else:
            try:
                result.append(self.op(self.left, self.right))
            except TypeError:
                return []
        return [DatumInContext.wrap(r) for r in result]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.left!r}{self.op}{self.right!r})"

    def __str__(self):
        return f"{self.left}{self.op}{self.right}"
