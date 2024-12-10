from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from filesystem import FileSystem
from database import initialize_database  # Correct import
from typing import List


app = FastAPI()

# Initialize the database when the app starts
@app.on_event("startup")
def startup_event():
    initialize_database()

# Instantiate the Filesystem
fs = FileSystem()

# Models for Input
class CopyMoveModel(BaseModel):
    source: str
    destination: str

# Define the input model for copying files/directories
class CopyModel(BaseModel):
    source: str
    destination: str
    preserve_attributes: bool = False
    verbose: bool = False
    is_directory: bool = False

class ChmodModel(BaseModel):
    path: str
    permissions: str
    
class CdModel(BaseModel):
    path: str

class EditFileModel(BaseModel):
    name: str            # File name to edit
    new_contents: str = None   # New content to save (optional)


class TouchModel(BaseModel):
    name: str  # File name for the touch operation

@app.get("/")
def root():
    """Lists available API routes."""
    routes = [{"path": route.path, "name": route.name, "methods": list(route.methods)} for route in app.routes]
    return {"available_routes": routes}

@app.get("/pwd")
def get_current_directory():
    """Returns the current working directory."""
    try:
        result = fs.pwd()
        return {"current_directory": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ls")
def list_files(all: bool = Query(False, alias='-a'), long_format: bool = Query(False, alias='-l'), human_readable: bool = Query(False, alias='-h')):
    """List files and directories in the current directory."""
    try:
        flags = []
        if all:
            flags.append('-a')
        if long_format:
            flags.append('-l')
        if human_readable:
            flags.append('-h')
        
        result = fs.ls(flags=flags)
        return {"files_and_dirs": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mkdir")
def create_directory(name: str):
    """Create a new directory."""
    try:
        result = fs.mkdir(name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cd")
def change_directory(payload: CdModel):
    # Change directory to the specified path
    try:
        fs.cd(payload.path)
        return {"message": f"Changed to directory '{fs.pwd()}'", "current_directory": fs.pwd()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/cp")
def copy(payload: CopyModel):
    """API to copy files or directories."""
    try:
        if payload.is_directory:
            # Call the function to copy a directory
            result = fs.copy_directory(payload.source, payload.destination, preserve_attributes=payload.preserve_attributes, verbose=payload.verbose)
        else:
            # Call the function to copy a file
            result = fs.copy_file(payload.source, payload.destination, preserve_attributes=payload.preserve_attributes, verbose=payload.verbose)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mv")
def move_file(payload: CopyMoveModel):
    """Move or rename a file."""
    try:
        result = fs.move_file(payload.source, payload.destination, user_id=1)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rm")
def remove_file(name: str):
    """Remove a file or directory."""
    try:
        result = fs.rm(name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cat")
def cat_file(
    names: List[str] = Query(...), 
    number_all_lines: bool = Query(False, alias='-n'),
    number_non_blank: bool = Query(False, alias='-b'),
    squeeze_blank: bool = Query(False, alias='-s'),
    show_ends: bool = Query(False, alias='-E'),
    show_tabs: bool = Query(False, alias='-T'),
    output_file: str = None
):
    """Display the contents of one or more files with optional flags, or save the output to a file."""
    try:
        # Build the flags list based on the query parameters
        flags = []
        if number_all_lines:
            flags.append('-n')
        if number_non_blank:
            flags.append('-b')
        if squeeze_blank:
            flags.append('-s')
        if show_ends:
            flags.append('-E')
        if show_tabs:
            flags.append('-T')

        # Pass the file names, flags, and output file to the cat method
        result = fs.cat(names, flags, output_file=output_file)

        # If the result is a success message (indicating the content was saved), return it
        if output_file:
            return {"message": result}
        
        # Otherwise, return the content for display
        return {"file_contents": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/head")
def head_file(name: str, lines: int = Query(10, alias='-n')):
    """Display the first 'n' lines of a file."""
    try:
        result = fs.head(name, lines)
        return {"head": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tail")
def tail_file(name: str, lines: int = Query(10, alias='-n')):
    """Display the last 'n' lines of a file."""
    try:
        result = fs.tail(name, lines)
        return {"tail": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/grep")
def grep(pattern: str, file: str):
    """Search for a pattern in a file."""
    try:
        result = fs.grep(pattern, file)
        return {"grep_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wc")
def word_count(file: str, lines: bool = Query(False, alias='-l'), words: bool = Query(False, alias='-w')):
    """Count lines or words in a file."""
    try:
        result = fs.word_count(file, lines, words)
        return {"word_count_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/touch")
def create_file(payload: TouchModel):
    """Create a new file (touch)."""
    try:
        result = fs.touch(payload.name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chmod")
def change_permissions(payload: ChmodModel):
    """Change file permissions."""
    try:
        result = fs.chmod(payload.path, payload.permissions)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/nano")
def edit_and_save_file(payload: EditFileModel):
    """Open a file, allow editing, and then save the changes."""
    try:
        # Load the current file contents or save the new content
        if payload.new_contents is None:
            # If no new contents provided, return the current contents for editing
            current_content = fs.edit_and_save_file(payload.name)
            return {"file_contents": current_content}  # Return contents for editing
        else:
            # If new contents are provided, append to existing content and save them
            result = fs.edit_and_save_file(payload.name, payload.new_contents)
            return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

