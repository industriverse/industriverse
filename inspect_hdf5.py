import h5py
import sys

def inspect(file_path):
    print(f"Inspecting: {file_path}")
    with h5py.File(file_path, 'r') as f:
        def print_structure(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  Dataset: {name} | Shape: {obj.shape} | Dtype: {obj.dtype}")
            elif isinstance(obj, h5py.Group):
                print(f"  Group: {name}")
        
        f.visititems(print_structure)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect(sys.argv[1])
    else:
        print("Usage: python inspect_hdf5.py <file>")
