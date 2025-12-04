import pickle
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader

class FossilBatchDataset(Dataset):
    def __init__(self, batch_dir: str):
        self.batch_files = list(Path(batch_dir).glob("*.pkl"))

    def __len__(self):
        return len(self.batch_files)

    def __getitem__(self, idx):
        with open(self.batch_files[idx], "rb") as f:
            batch = pickle.load(f)
        return (
            batch["tnn_ready_tensor"],
            batch["ebdm_ready_tensor"],
            batch["negentropy_score"],
        )

class FossilBatchLoader:
    def __init__(self, batch_dir: str, batch_size: int = 1, workers: int = 0):
        # workers=0 for safety in some envs, can increase for speed
        self.dataset = FossilBatchDataset(batch_dir)
        self.loader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            num_workers=workers,
            pin_memory=False, # Set True if using CUDA
            collate_fn=self.collate_batches # Custom collate might be needed if batches vary
        )

    def collate_batches(self, batch_list):
        # Since each item in the dataset IS a batch (tensor), 
        # the DataLoader will try to stack them.
        # If batch_size=1, we just return the first item.
        # If batch_size > 1, we concatenate the tensors.
        tnn_tensors = [b[0] for b in batch_list]
        ebdm_tensors = [b[1] for b in batch_list]
        negentropy_scores = [b[2] for b in batch_list]
        
        return (
            torch.cat(tnn_tensors, dim=0),
            torch.cat(ebdm_tensors, dim=0),
            torch.tensor(negentropy_scores)
        )

    def stream(self):
        for batch in self.loader:
            yield batch
