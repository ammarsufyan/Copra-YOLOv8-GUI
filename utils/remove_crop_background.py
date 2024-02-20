import os
from PIL import Image
from rembg import remove


def remove_crop_background(input_dir: str, output_dir: str):
    """
    Remove background from images in input_dir and save the result in output_dir.

    Args:
        input_dir (str): Path to the directory containing images to be processed.
        output_dir (str): Path to the directory where the processed images will be saved.
    """

    # Traverse through the input directory and its subdirectories
    for root, _, files in os.walk(input_dir):
        for file in files:
            # Get the input and output paths for the current file
            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(input_path, input_dir)
            output_path = os.path.splitext(os.path.join(output_dir, relative_path))[0] + ".png"

            # Check if the output file already exists else process the input file
            if os.path.exists(output_path):
                print(f"Skipping {input_path} because {output_path} already exists")
            else:
                # Create the output directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                print(f"Processing {input_path} and saving it to {output_path}")
                # Open the input files
                with Image.open(input_path) as img:
                    # Remove the background and crop the input image
                    output = remove(img)
                    output = output.crop(output.getbbox())
                    # Resize image to 640x640 pixels
                    output = output.resize((640, 640))
                    # Save the output as PNG
                    output.save(output_path, "png")