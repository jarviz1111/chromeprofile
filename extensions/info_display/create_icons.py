import os
from PIL import Image, ImageDraw, ImageFont

# Ensure the icons directory exists
os.makedirs("icons", exist_ok=True)

# Function to create a simple icon
def create_icon(size, filename):
    # Create a new image with a blue background
    img = Image.new('RGBA', (size, size), (66, 133, 244, 255))
    draw = ImageDraw.Draw(img)
    
    # Calculate circle size
    circle_size = size // 2
    
    # Draw a white circle in the center
    circle_x = size // 2
    circle_y = size // 2
    circle_radius = circle_size // 2
    draw.ellipse(
        (circle_x - circle_radius, circle_y - circle_radius, 
         circle_x + circle_radius, circle_y + circle_radius),
        fill=(255, 255, 255, 255)
    )
    
    # Draw a magnifying glass handle
    handle_width = circle_radius // 3
    handle_start_x = circle_x + circle_radius * 0.7
    handle_start_y = circle_y + circle_radius * 0.7
    handle_end_x = circle_x + circle_radius * 1.5
    handle_end_y = circle_y + circle_radius * 1.5
    
    draw.line(
        (handle_start_x, handle_start_y, handle_end_x, handle_end_y),
        fill=(255, 255, 255, 255),
        width=handle_width
    )
    
    # Save the image
    img.save(filename)
    print(f"Created icon: {filename}")

# Create icons in different sizes
create_icon(16, "icons/icon16.png")
create_icon(48, "icons/icon48.png")
create_icon(128, "icons/icon128.png")

print("All icons created successfully.")