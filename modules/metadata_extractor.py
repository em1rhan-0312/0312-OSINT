import os
from PIL import Image
from PIL.ExifTags import TAGS
from modules import display as disp

class MetadataExtractor:
    def extract_exif(self, image_path):
        try:
            image = Image.open(image_path)
            info = image._getexif()
            
            if info is None:
                disp.perror("No EXIF metadata found in this image.")
                return

            disp.pheader(f"METADATA FOR: {os.path.basename(image_path)}")
            
            for tag_id, value in info.items():
                tag = TAGS.get(tag_id, tag_id)
                disp.pout(f"{tag}: ", disp.YELLOW)
                disp.pout(f"{value}\n", disp.WHITE)
                
        except Exception as e:
            disp.perror(f"Error reading image: {e}")

def run_metadata_extractor():
    disp.pheader("IMAGE METADATA EXTRACTOR")
    path = disp.pin("Enter full path to image file: ")
    if os.path.exists(path):
        extractor = MetadataExtractor()
        extractor.extract_exif(path)
    else:
        disp.perror("File not found!")
