# __init__.py for storage_interface

from .base_storage_adapter import BaseStorageAdapter, StorageAdapterInterface
# Import specific adapters when they are created, e.g.:
# from .timeseries_db_adapter import TimeseriesDBAdapter
# from .metadata_store_adapter import MetadataStoreAdapter

__all__ = [
    "BaseStorageAdapter",
    "StorageAdapterInterface",
    # "TimeseriesDBAdapter",
    # "MetadataStoreAdapter"
]

