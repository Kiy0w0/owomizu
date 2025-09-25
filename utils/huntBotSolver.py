import glob
import os
import numpy as np
import aiohttp
import io
from PIL import Image
import requests

"""
Made with the help of https://github.com/realphandat/phandat-selfbot/blob/main/owo/modules.py
I have recieved permission to use this code snippet.
"""


async def solveHbCaptcha(captcha_url, session):
    checks = []
    """
    I tried my best to make these work without folder seperation but uhh failed lol.
     ill think of a way later but hey, it works somehow with folder seperation
    """ 
    try:
        check_images = glob.glob("static/imgs/corpus/**/*.png")
        if not check_images:
            print("❌ No captcha corpus images found in static/imgs/corpus/")
            return ""
        
        for check_image in sorted(check_images):
            try:
                img = Image.open(check_image)
                checks.append((img, img.size, os.path.basename(check_image).split(".")[0]))
            except Exception as e:
                print(f"❌ Error loading corpus image {check_image}: {e}")
                continue
                
        if not checks:
            print("❌ No valid corpus images loaded for captcha solving")
            return ""
            
        print(f"✅ Loaded {len(checks)} corpus images for captcha solving")
    except Exception as e:
        print(f"❌ Error loading captcha corpus: {e}")
        return ""
    
    """
    the above is basically the size, img and path (name to be used if matched)
    """
    try:
        # get img, aiohttp session passed from main file
        # iam not making the mistake of making session each time lol.
        print(f"🔍 Fetching captcha image from: {captcha_url}")
        async with session.get(captcha_url) as resp:
            if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                large_image = Image.open(io.BytesIO(await resp.read()))
                large_array = np.array(large_image)
                print(f"✅ Captcha image loaded successfully - size: {large_image.size}")
            else:
                print(f"❌ Failed to fetch a valid image. Status: {resp.status}, Content-Type: {resp.headers.get('Content-Type')}")
                return ""

    except Exception as e:
        print(f"❌ Error fetching the captcha image: {e}")
        return ""
    matches = []
    print(f"🔍 Starting captcha pattern matching with {len(checks)} corpus images...")
    
    try:
        for img, (small_w, small_h), letter in checks:
            small_array = np.array(img)
            """
            This mask part makes sure transparent part are not compared.
            with this the captcha can be easily solved.
            """
            if small_array.shape[2] >= 4:  # Check if alpha channel exists
                mask = small_array[:, :, 3] > 0  # Alpha mask for non-transparent pixels
            else:
                # Fallback for images without alpha channel
                mask = np.ones((small_h, small_w), dtype=bool)

            for y in range(large_array.shape[0] - small_h + 1):
                for x in range(large_array.shape[1] - small_w + 1):
                    segment = large_array[y : y + small_h, x : x + small_w]
                    try:
                        if segment.shape == small_array.shape and np.array_equal(segment[mask], small_array[mask]):
                            """
                            prevents matching of letters close with prev matched letters
                            """
                            if not any(
                                (m[0] - small_w < x < m[0] + small_w)
                                and (m[1] - small_h < y < m[1] + small_h)
                                for m in matches
                            ):
                                matches.append((x, y, letter))
                                print(f"✅ Found match: '{letter}' at position ({x}, {y})")
                    except Exception as e:
                        # Skip this comparison if there's a shape mismatch
                        continue
                        
        matches = sorted(matches, key=lambda tup: tup[0])
        result = "".join([i[2] for i in matches])
        
        if result:
            print(f"🎯 Captcha solved successfully: '{result}' (found {len(matches)} characters)")
        else:
            print(f"❌ No matches found - captcha solving failed")
            
        return result
    except Exception as e:
        print(f"❌ Error during captcha pattern matching: {e}")
        return ""
