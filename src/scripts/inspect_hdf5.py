import h5py
import sys

def inspect_file(path):
    try:
        with h5py.File(path, 'r') as f:
            print(f"Keys in {path}:")
            def print_attrs(name, obj):
                if isinstance(obj, h5py.Dataset):
                    print(f"{name}: {obj.shape}")
                else:
                    print(name)
            f.visititems(print_attrs)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_file(sys.argv[1])
    else:
        print("Usage: python inspect_hdf5.py <path>")
