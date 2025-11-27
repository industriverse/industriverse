import h5py
import argparse
import os

def inspect_hdf5(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"=== Inspecting HDF5: {file_path} ===")
    
    try:
        with h5py.File(file_path, 'r') as f:
            def print_structure(name, obj):
                indent = "  " * (name.count('/') + 1)
                if isinstance(obj, h5py.Dataset):
                    print(f"{indent}Dataset: {name} | Shape: {obj.shape} | Type: {obj.dtype}")
                elif isinstance(obj, h5py.Group):
                    print(f"{indent}Group: {name}")
            
            f.visititems(print_structure)
            
    except Exception as e:
        print(f"Error reading HDF5: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect HDF5 file structure.")
    parser.add_argument("path", help="Path to the .hdf5 file")
    args = parser.parse_args()
    
    inspect_hdf5(args.path)
