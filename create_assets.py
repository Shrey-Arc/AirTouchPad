from PIL import Image, ImageDraw, ImageFont
import os

# Create directories
os.makedirs('assets/screenshots', exist_ok=True)

# Create logo (400x400)
img = Image.new('RGB', (400, 400), color='#89b4fa')
draw = ImageDraw.Draw(img)

# Draw a hand shape
draw.ellipse([100, 80, 300, 280], fill='white')  # Palm
draw.ellipse([120, 60, 160, 100], fill='white')  # Thumb
draw.ellipse([180, 40, 220, 90], fill='white')   # Index
draw.ellipse([230, 40, 270, 90], fill='white')   # Middle
draw.ellipse([280, 50, 310, 100], fill='white')  # Ring

# Save logo
img.save('assets/logo.png')
print("✓ Logo created")

# Convert to icon
img_resized = img.resize((256, 256), Image.LANCZOS)
img_resized.save('assets/icon.ico', format='ICO', sizes=[(256, 256)])
print("✓ Icon created")

# Create screenshot placeholders
def create_placeholder(filename, title, color='#1e1e2e'):
    img = Image.new('RGB', (800, 600), color=color)
    draw = ImageDraw.Draw(img)
    
    # Draw title
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    # Center text
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (800 - text_width) / 2
    y = (600 - text_height) / 2
    
    draw.text((x, y - 50), title, fill='#89b4fa', font=font)
    draw.text((x, y + 50), "Screenshot placeholder", fill='#cdd6f4', font=small_font)
    
    img.save(f'assets/screenshots/{filename}')
    print(f"✓ {filename} created")

# Create all screenshot placeholders
create_placeholder('main_interface.png', 'Main Interface')
create_placeholder('installer.png', 'Installation Wizard')
create_placeholder('tutorial.png', 'Gesture Tutorial')
create_placeholder('debug_overlay.png', 'Debug Overlay')

print("\n✅ All assets created successfully!")