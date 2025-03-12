from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon():
    # Create a new image with a black background
    size = (32, 32)
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a blue rectangle as background
    draw.rectangle([(0, 0), (32, 32)], fill='#0066cc')
    
    # Draw "V" in white
    draw.polygon([(8, 8), (14, 24), (20, 8)], fill='white')
    
    # Save as ICO
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    image.save(os.path.join(static_dir, 'favicon.ico'), format='ICO', sizes=[(32, 32)])

if __name__ == '__main__':
    create_favicon() 