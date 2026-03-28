#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

MODE="${1:-smoke}"
ACTION="${2:-all}"

SMOKE_KAGGLE_HANDLE="${ASL_SMOKE_KAGGLE_HANDLE:-ayuraj/asl-dataset}"
FULL_KAGGLE_HANDLE="${ASL_FULL_KAGGLE_HANDLE:-ayuraj/american-sign-language-dataset}"
WEIGHTS_PATH="${ROOT_DIR}/ml/models/asl_landmark_model.pt"
DATASET_PATH_OVERRIDE="${ASL_DATASET_PATH:-}"
EXTRA_DATASET_PATHS="${ASL_EXTRA_DATASET_PATHS:-}"
CAMERA_INDEX="${ASL_CAMERA_INDEX:--1}"

usage() {
  cat <<'EOF'
Usage:
  ./run_asl.sh [smoke|full] [all|train-only|live-only|ui-only]

Examples:
  ./run_asl.sh
  ./run_asl.sh smoke
  ./run_asl.sh smoke train-only
  ./run_asl.sh smoke ui-only
  ./run_asl.sh full

  Notes:
  smoke uses a smaller Kaggle ASL dataset for a faster first run.
  full uses the larger American Sign Language dataset.
  Set ASL_DATASET_PATH=/path/to/extracted/dataset to use a local dataset instead.
  Set ASL_EXTRA_DATASET_PATHS with colon-separated dataset folders to combine more local datasets.
  Set ASL_CAMERA_INDEX=1 if your webcam is not on the default index.
EOF
}

ensure_environment() {
  if [[ ! -x ".venv/bin/python" ]]; then
    echo "Missing virtual environment. Create it with:"
    echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
  fi

  if ! .venv/bin/python -c "import kagglehub, mediapipe, cv2, torch" >/dev/null 2>&1; then
    echo "Missing Python dependencies in .venv. Install them with:"
    echo "  source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
  fi
}

dataset_handle_for_mode() {
  if [[ "$MODE" == "smoke" ]]; then
    printf '%s\n' "$SMOKE_KAGGLE_HANDLE"
  elif [[ "$MODE" == "full" ]]; then
    printf '%s\n' "$FULL_KAGGLE_HANDLE"
  else
    usage
    exit 1
  fi
}

cache_dir_for_handle() {
  local handle="$1"
  local owner="${handle%%/*}"
  local dataset="${handle##*/}"
  printf '%s\n' "${HOME}/.cache/kagglehub/datasets/${owner}/${dataset}"
}

clean_incomplete_kaggle_cache() {
  local handle="$1"
  local cache_dir
  cache_dir="$(cache_dir_for_handle "$handle")"
  local archive_path="${cache_dir}/1.archive"
  local version_dir="${cache_dir}/versions/1"
  local complete_marker="${cache_dir}/1.complete"

  if [[ -f "$archive_path" && ! -e "$complete_marker" ]]; then
    echo "Removing incomplete Kaggle cache so the dataset can be downloaded cleanly..."
    rm -f "$archive_path"
    rm -rf "$version_dir"
  fi
}

train_model() {
  mkdir -p ml/models
  local handle
  handle="$(dataset_handle_for_mode)"

  local train_args=(
    --output "$WEIGHTS_PATH"
  )

  if [[ -n "$DATASET_PATH_OVERRIDE" ]]; then
    train_args+=(
      --dataset "$DATASET_PATH_OVERRIDE"
    )
  else
    clean_incomplete_kaggle_cache "$handle"
    train_args+=(
      --kaggle-handle "$handle"
    )
  fi

  if [[ -n "$EXTRA_DATASET_PATHS" ]]; then
    local old_ifs="$IFS"
    IFS=':'
    for extra_path in $EXTRA_DATASET_PATHS; do
      if [[ -n "$extra_path" ]]; then
        train_args+=(
          --dataset "$extra_path"
        )
      fi
    done
    IFS="$old_ifs"
  fi

  if [[ "$MODE" == "smoke" ]]; then
    train_args+=(
      --max-samples-per-class 10
      --augmentations-per-image 1
      --epochs 2
    )
  else
    train_args+=(
      --hidden-sizes 512,256,128
      --dropout 0.25
      --epochs 40
      --augmentations-per-image 3
    )
  fi

  PYTHONPATH=ml/src .venv/bin/python -m asl_recognizer.train "${train_args[@]}"
}

run_live_inference() {
  if [[ ! -f "$WEIGHTS_PATH" ]]; then
    echo "Missing model weights at $WEIGHTS_PATH"
    echo "Run training first with:"
    echo "  ./run_asl.sh $MODE train-only"
    exit 1
  fi

  PYTHONPATH=ml/src .venv/bin/python -m asl_recognizer.live_inference --weights "$WEIGHTS_PATH" --camera "$CAMERA_INDEX"
}

run_ui() {
  if [[ ! -f "$WEIGHTS_PATH" ]]; then
    echo "Missing model weights at $WEIGHTS_PATH"
    echo "Run training first with:"
    echo "  ./run_asl.sh $MODE train-only"
    exit 1
  fi

  PYTHONPATH=ml/src .venv/bin/python -m asl_recognizer.ui_app --weights "$WEIGHTS_PATH" --camera "$CAMERA_INDEX"
}

main() {
  case "$ACTION" in
    all|train-only|live-only|ui-only) ;;
    *)
      usage
      exit 1
      ;;
  esac

  ensure_environment

  case "$ACTION" in
    train-only)
      train_model
      ;;
    live-only)
      run_live_inference
      ;;
    ui-only)
      run_ui
      ;;
    all)
      if [[ -f "$WEIGHTS_PATH" ]]; then
        echo "Using existing model weights at $WEIGHTS_PATH"
      else
        train_model
      fi
      run_live_inference
      ;;
  esac
}

main "$@"
