#!/bin/bash

set -e  # Exit on error

# === Prompt user for input ===
read -rp "Enter path to config directory: " config_dir
read -rp "Enter path to old blf_cli tool: " old_blf_cli
read -rp "Enter path to new blf_cli tool: " new_blf_cli
read -rp "Enter game title (e.g., Halo 3): " title
read -rp "Enter build version (e.g., 12070.08.09.05.2031.halo3_ship): " version

# Echo initial details
echo "Upgrading configuration for $title version $version"
echo "Config path: $config_dir"

# Create a temporary directory for build output
build_dir=$(mktemp -d)
echo "Using temporary build_dir: $build_dir"

# Ensure cleanup on exit
cleanup() {
  echo "Cleaning up temporary build_dir..."
  rm -rf "$build_dir"
}
trap cleanup EXIT

# Step 1: Build binaries from configuration
echo "== Step 1: Building binary files from configuration =="
"$old_blf_cli" title-storage build "$config_dir" "$build_dir" "$title" "$version"
echo "== Done building binary files =="

# Step 2: Export game and map variants
export_variants() {
  local variant_type="$1"

  # Process each "hopper folder"
  find "$config_dir" -type d -name "$variant_type" | while read -r input_dir; do
    hopper_folder=$(basename "$(dirname "$input_dir")")
    output_dir="$build_dir/$hopper_folder/$variant_type"
    mkdir -p "$output_dir"
    echo "Exporting variants to $output_dir"

    for json_file in "$input_dir"/*.json; do
      filename=$(basename "$json_file" .json)
      output_file="$output_dir/${filename}.bin"
      echo "Exporting $json_file"
      "$old_blf_cli" title-storage export-variant "$json_file" "$output_file" "$title" "$version"
    done
  done
}

echo "== Step 2: Exporting game and map variants =="
export_variants "map_variants"
export_variants "game_variants"
echo "== Done exporting variants =="

# Step 3: Build configuration from binary files
echo "== Step 3: Building configuration from binary files =="
"$new_blf_cli" title-storage build-config "$build_dir" "$config_dir" "$title" "$version"
echo "== Done building configuration =="

# Step 4: Import variants back into config
import_variants() {
  local variant_type="$1"

  for hopper_path in "$build_dir"/*/; do
    hopper_folder=$(basename "$hopper_path")
    variant_path="$build_dir/$hopper_folder/$variant_type"
    
    if [ -d "$variant_path" ]; then
      echo "Processing $hopper_folder/$variant_type"

      for bin_file in "$variant_path"/*.bin; do
        echo "Importing $config_dir/$hopper_folder"
        "$new_blf_cli" title-storage import-variant "$config_dir/$hopper_folder" "$bin_file" "$title" "$version"
      done
    fi
  done
}

echo "== Step 4: Importing variants into configuration =="
import_variants "map_variants"
import_variants "game_variants"
echo "== Done importing variants =="
