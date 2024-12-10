from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from filesystem import FileSystem
from database import initialize_database  # Correct import
from typing import List,Optional


app = FastAPI()

# Initialize the database when the app starts
@app.on_event("startup")
def startup_event():
    initialize_database()

# Instantiate the Filesystem
fs = FileSystem()



# Define the input model for copying files/directories
class CopyModel(BaseModel):
    source: str
    destination: str
    is_directory: bool = False
    
class MkdirRequest(BaseModel):
    path: str  



class CdModel(BaseModel):
    path: str

class EditFileModel(BaseModel):
    name: str            # File name to edit
    new_contents: str = None   # New content to save (optional)
    mode: str = 'append'  # 'append' or 'overwrite'

class TouchModel(BaseModel):
    name: str  # File name for the touch operation

@app.get("/")
def root():
    """Lists available API routes."""
    routes = [{"path": route.path, "name": route.name, "methods": list(route.methods)} for route in app.routes]
    return {"available_routes": routes}

@app.get("/pwd")
def get_current_directory():
    """
    Returns the current working directory using the FileSystem class.
    """
    try:
        current_directory = fs.pwd()
        return {"current_directory": current_directory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ls")
def list_files(
    all: bool = Query(False, alias='-a'), 
    long_format: bool = Query(False, alias='-l'), 
    human_readable: bool = Query(False, alias='-h')
):
    """
    List files and directories in the current directory.
    Flags:
    - `-a`: Show hidden files
    - `-l`: Use a long listing format
    - `-h`: Print human-readable file sizes
    """
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
def create_directory(request: MkdirRequest):
    """Create a new directory at the specified path in the virtual filesystem."""
    try:
        result = fs.mkdir(request.path)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
           
@app.get("/current_user")
def get_current_user():
    """API to get the current user."""
    try:
        result = fs.get_current_user()
        return {"username": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cd")
def change_directory(payload: CdModel):
    """
    Change directory to the specified path.
    """
    try:
        result = fs.cd(payload.path)  # Call the `cd` method from the `FileSystem` class
        return {"message": result, "current_directory": fs.pwd()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Directory '{payload.path}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cp")
def copy(payload: CopyModel):
    """API to copy files or directories."""
    try:
        # Check if the item to be copied is a directory
        result = fs.copy_File_Directory(payload.source, payload.destination, payload.is_directory)
        return {"message": result}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define the model for receiving request payload
class CopyMoveModel(BaseModel):
    source: str
    destination: str
    isdirectory: bool

@app.post("/mv")
def move(payload: CopyMoveModel):
    """Move or rename a file or directory."""
    try:
        result = fs.mv(payload.source, payload.destination, payload.isdirectory)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/rm")
def remove_file(path: str, recursive: bool = Query(False, alias="-r")):
    """
    Remove a file or directory.

    Arguments:
    - `path`: The path to the file or directory.
    - `recursive`: Whether to remove the directory recursively (if it's a directory).
    """
    try:
        result = fs.rm(path, recursive)  # Call the rm function from FileSystem class
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IsADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"rm: cannot remove '{path}': Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cat")
def cat_file(names: List[str] = Query(...)):
    """Concatenate and display the contents of one or more files."""
    try:
        result = fs.cat(names)
        return {"file_contents": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"One or more files not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@app.get("/grep")
def grep(pattern: str, file: str):
    """Search for a pattern in a file."""
    try:
        result = fs.grep(pattern, file)
        return {"grep_result": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wc")
def word_count(file: str, lines: bool = Query(False, alias='-l'), words: bool = Query(False, alias='-w')):
    """Count lines or words in a file."""
    try:
        result = fs.word_count(file, lines, words)
        return {"word_count_result": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/touch")
def create_file(payload: TouchModel):
    """Create a new file (touch)."""
    try:
        # Use the resolved virtual path directly
        result = fs.touch(payload.name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChmodRequest(BaseModel):
    permissions: str
    path: str

@app.put("/chmod")
async def change_permissions(chmod_request: ChmodRequest):
    """Change permissions of a specified file or directory."""
    permissions = chmod_request.permissions
    path = chmod_request.path

    try:
        # Convert the permissions to a format the database can understand
        permissions_value = int(permissions, 8)  # Convert from string to integer

        # Call the chmod method from the FileSystem class
        result = fs.chmod(path, permissions_value)  # This assumes you have the chmod method in your FileSystem class

        return {"detail": f"Permissions of '{path}' changed to '{permissions}'."}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            # Handle mode: 'append' or 'overwrite'
            if payload.mode == 'overwrite':
                result = fs.overwrite_file(payload.name, payload.new_contents)
            else:
                result = fs.edit_and_save_file(payload.name, payload.new_contents)  # Appending
            return {"message": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{payload.name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TailModel(BaseModel):
    file_name: str
    num_lines: int = 10

@app.post("/tail")
def tail_file(payload: TailModel):
    """
    Fetch the last N lines of a file from the virtual filesystem.
    """
    try:
        # Call the `tail` method from the filesystem
        result = fs.tail(payload.file_name, payload.num_lines)
        return {"content": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{payload.file_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HeadModel(BaseModel):
    file_name: str
    num_lines: int = 10

@app.post("/head")
def tail_file(payload: HeadModel):
    """
    Fetch the first N lines of a file from the virtual filesystem.
    """
    try:
        # Call the `tail` method from the filesystem
        result = fs.head(payload.file_name, payload.num_lines)
        return {"content": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{payload.file_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
