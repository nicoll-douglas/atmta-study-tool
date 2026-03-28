from atmta_study_tool.language import Word, SymbolLike
from .models import State

# a "symbol-like" object for an FSA transitions i.e a Symbol, the UID of a Symbol, or a Word (epsilon)
type FSASymbolLike = SymbolLike | Word

# a "state-like" object i.e a State or the UID of a State
type StateLike = State | str
