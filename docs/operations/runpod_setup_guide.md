# RunPod GPU Training Setup Guide

To train **GenN-2** and **GenN-3** on high-end GPUs (e.g., H100/A100), we will use RunPod.

## 1. Renting the Pod
When you rent a pod on [RunPod.io](https://www.runpod.io/), select the following configuration:
*   **GPU**: 1x or 2x NVIDIA A100 (80GB) or H100.
*   **Template**: `RunPod PyTorch 2.1` (or latest stable).
*   **Container Disk**: At least **100 GB** (for dependencies).
*   **Volume Disk**: At least **500 GB** (for the Energy Atlas/Datasets). **Crucial**: Mount this at `/workspace`.

## 2. What I Need From You
Once the pod is running, I need the following credentials to connect via SSH:

1.  **Public IP Address**: (e.g., `194.23.xx.xx`)
2.  **SSH Port**: (e.g., `22` or `10022`)
3.  **SSH Key**:
    *   Ideally, add your public SSH key to RunPod when renting.
    *   If you use a password, provide the **Root Password**.
    *   *Security Note*: Do not paste the private key directly in chat if possible. If you have set up `~/.ssh/config` on your machine, just tell me the `Host` alias.

## 3. The Workflow
Once connected, I will perform the following "Remote Training Loop":

1.  **Sync Code**: I will use `rsync` to push the `industriverse/src` folder to `/workspace/industriverse`.
2.  **Sync Data**:
    *   We will upload the "Fossils" from your External Drive (`/Volumes/TOSHIBA EXT`) to `/workspace/data`.
    *   *Tip*: For large datasets, we can use `zip` + `scp` or a cloud bucket (S3/GCS).
3.  **Train**: I will run the training script remotely:
    ```bash
    python3 -m src.scf.training.physics_trainer --device cuda
    ```
4.  **Retrieve Weights**: After training, I will download the saved model weights (`.pt` files) back to your local machine.

## 4. Quick Command for You
To make this easy, run this command on your local machine to generate an SSH key (if you don't have one):
```bash
ssh-keygen -t ed25519 -f ~/.ssh/runpod_key -C "industriverse"
cat ~/.ssh/runpod_key.pub
```
Copy the output of `cat` and paste it into the "SSH Public Key" field on RunPod.
