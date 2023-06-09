import PIL.Image as im

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# resize image 
def resize_image(image, new_width=75):
    width, height = image.size
    ratio = height / width 
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return(resized_image)

# pixels to a string of ascii 
def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
    return(characters)  

# grayscale
def gray(image):
    grayscale_image = image.convert("L")
    return(grayscale_image)  

def main(new_width=75):
    # open image from user-input
    path = input("Enter a valid pathname to an image:\n")
    try:
        image = im.open(path)
    
    except:
        print(path, " is not a valid pathname to an image.")
        return
  
    # convert image to ascii    
    new_image_data = pixels_to_ascii(gray(resize_image(image)))
    
    # format
    pixel_count = len(new_image_data)  
    ascii_image = "\n".join([new_image_data[index:(index+new_width)] for index in range(0, pixel_count, new_width)])
    
    print(ascii_image)
    
    # save 
    with open("ascii_image.txt", "w") as f:
        f.write(ascii_image)
 
# run
main()