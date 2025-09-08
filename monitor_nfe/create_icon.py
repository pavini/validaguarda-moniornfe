#!/usr/bin/env python3
"""
Script para criar um ícone simples para o app NFe Monitor
"""

def convert_existing_icon():
    """Convert existing icon.png to platform-specific formats"""
    try:
        from PIL import Image
        import platform
        
        if not Path('icon.png').exists():
            print("❌ icon.png não encontrado")
            return False
            
        print("🔄 Convertendo icon.png existente...")
        img = Image.open('icon.png')
        
        # Ensure it's RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create macOS ICNS if on Mac
        if platform.system() == 'Darwin':
            try:
                import subprocess
                subprocess.run(['mkdir', '-p', 'icon.iconset'], check=True)
                
                sizes = [16, 32, 64, 128, 256, 512]
                for s in sizes:
                    resized = img.resize((s, s), Image.Resampling.LANCZOS)
                    resized.save(f'icon.iconset/icon_{s}x{s}.png')
                    if s <= 256:
                        resized.save(f'icon.iconset/icon_{s}x{s}@2x.png')
                
                subprocess.run(['iconutil', '-c', 'icns', 'icon.iconset'], check=True)
                subprocess.run(['rm', '-rf', 'icon.iconset'], check=True)
                print("✅ macOS icon created: icon.icns")
            except Exception as e:
                print(f"⚠️  Could not create ICNS: {e}")
        
        # Create Windows ICO
        try:
            ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save('icon.ico', format='ICO', sizes=ico_sizes)
            print("✅ Windows icon created: icon.ico")
        except Exception as e:
            print(f"⚠️  Could not create ICO: {e}")
            
        return True
            
    except Exception as e:
        print(f"❌ Error converting icon: {e}")
        return False

def create_simple_icon():
    try:
        from PIL import Image, ImageDraw, ImageFont
        import platform
        
        # Create 256x256 icon
        size = 256
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(33, 150, 243), outline=(21, 101, 192), width=4)
        
        # Draw "NFe" text
        try:
            font_size = 60
            font = ImageFont.truetype("Arial", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "NFe"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 10
        
        draw.text((x, y), text, fill='white', font=font)
        
        # Draw validation checkmark
        check_size = 40
        check_x = size - check_size - 30
        check_y = size - check_size - 30
        
        draw.ellipse([check_x, check_y, check_x + check_size, check_y + check_size], 
                    fill=(76, 175, 80))
        
        # Simple checkmark
        draw.line([check_x + 10, check_y + 20, check_x + 18, check_y + 28], 
                 fill='white', width=3)
        draw.line([check_x + 18, check_y + 28, check_x + 30, check_y + 12], 
                 fill='white', width=3)
        
        # Save as PNG
        img.save('icon.png', 'PNG')
        print("✅ Icon created: icon.png")
        
        # Create macOS ICNS if on Mac
        if platform.system() == 'Darwin':
            try:
                import subprocess
                # Create iconset directory
                subprocess.run(['mkdir', '-p', 'icon.iconset'], check=True)
                
                # Generate different sizes
                sizes = [16, 32, 64, 128, 256, 512]
                for s in sizes:
                    resized = img.resize((s, s), Image.Resampling.LANCZOS)
                    resized.save(f'icon.iconset/icon_{s}x{s}.png')
                    if s <= 256:
                        resized.save(f'icon.iconset/icon_{s}x{s}@2x.png')
                
                # Convert to ICNS
                subprocess.run(['iconutil', '-c', 'icns', 'icon.iconset'], check=True)
                subprocess.run(['rm', '-rf', 'icon.iconset'], check=True)
                print("✅ macOS icon created: icon.icns")
            except Exception as e:
                print(f"⚠️  Could not create ICNS: {e}")
        
        # Create Windows ICO
        try:
            ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            img.save('icon.ico', format='ICO', sizes=ico_sizes)
            print("✅ Windows icon created: icon.ico")
        except Exception as e:
            print(f"⚠️  Could not create ICO: {e}")
            
    except ImportError:
        print("⚠️  PIL (Pillow) not installed. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False
    
    return True

if __name__ == "__main__":
    from pathlib import Path
    
    # Check for logo files first
    logo_files = ['logo-validatech.png', 'icon.png']
    source_file = None
    
    for logo_file in logo_files:
        if Path(logo_file).exists():
            source_file = logo_file
            break
    
    if source_file:
        print(f"📄 {source_file} encontrado - convertendo para formatos específicos...")
        # Temporarily rename to icon.png for conversion if needed
        if source_file != 'icon.png':
            from shutil import copy2
            copy2(source_file, 'icon.png')
        convert_existing_icon()
    else:
        print("🎨 Criando ícone padrão...")
        create_simple_icon()