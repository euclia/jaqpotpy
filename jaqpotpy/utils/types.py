from typing import Any, Callable, List, Sequence, Tuple, TypeVar, Union
import numpy as np

T = TypeVar("T")

# An activation function for a layer: either a function or the name of a standard activation
ActivationFn = Union[Callable, str]

# A loss function for use with KerasModel or TorchModel: f(outputs, labels, weights)
LossFn = Callable[[List, List, List], Any]

# A single value of some type, or multiple values of that type
OneOrMany = Union[T, Sequence[T]]

# The shape of a NumPy array
Shape = Tuple[int, ...]

# A NumPy array, or an object that can be converted to one.  Once we move to
# requiring NumPy 1.20, we should replace this with numpy.typing.ArrayLike.
ArrayLike = Union[np.ndarray, Sequence]

# type of RDKit object
RDKitMol = Any
RDKitAtom = Any
RDKitBond = Any

# type of Pymatgen object
PymatgenStructure = Any
PymatgenComposition = Any
