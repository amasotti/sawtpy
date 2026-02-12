import torch

def main():
    print("Hello from experiment!")

    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("GPU acceleration (MPS) is available.")
    else:
        print("MPS not available. Using CPU.")


if __name__ == "__main__":
    main()
