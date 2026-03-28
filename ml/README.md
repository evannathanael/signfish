# ML Workspace

This folder contains the ASL model training workflow.

## Main pieces

- `src/asl_recognizer/`: landmark-based ASL recognition package
- `data/`: external, raw, and processed datasets
- `models/`: exported trained model artifacts
- `scripts/`: training and preprocessing entrypoints

## Current model

The current ASL alphabet classifier uses MediaPipe hand landmarks plus a PyTorch MLP classifier. It supports the static ASL letters:

`A B C D E F G H I K L M N O P Q R S T U V W X Y`

## Training

Use the root launcher for easiest training:

```bash
./run_asl.sh full train-only
```

Or run the trainer directly:

```bash
PYTHONPATH=ml/src .venv/bin/python -m asl_recognizer.train --help
```
