from src.creator.outlines.master_outline_compiler import MasterOutlineCompiler
from db.db import DB, Outline

outline = DB.get(Outline, 10)
compiler = MasterOutlineCompiler(outline.id)

outline = compiler.compile()
