# install color math:
# sudo pip install colormath
# ref: https://en.wikipedia.org/wiki/CIE_1931_color_space
# http://hanzratech.in/2015/01/16/color-difference-between-2-colors-using-python.html
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# compare the difference of two colors
# return a list of four floats,
# 1.  distance of two color in color spectrum space.
# 2.  difference of r - cutoff
# 3.  difference of g - cutoff
# 4.  difference of b - cutoff
def compare_rgb(rgb1, rgb2):
    color1_rgb = sRGBColor(rgb1[0]/255, rgb1[1]/255, rgb1[2]/255);
    color2_rgb = sRGBColor(rgb2[0]/255, rgb2[1]/255, rgb2[2]/255);

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor);

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor);

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab);
    m1 = min(rgb1) # cutoff is the min of three
    m2 = min(rgb2)
    delta_r = abs((rgb1[0]-m1) - (rgb2[0]-m2))
    delta_g = abs((rgb1[1]-m1) - (rgb2[1]-m2))
    delta_b = abs((rgb1[2]-m1) - (rgb2[2]-m2))
    return (delta_e, delta_r, delta_g, delta_b)

if __name__ == "__main__":

    for c in range(255):
        color1 = (128,128,128)
        color2 = (c,c,c)
        delta = compare_rgb(color1, color2)
        print(f"color {color1}, {color2} = {delta}")


    delta = compare_rgb((255,0,0),(0,0,255))
    print ("The difference between the 2 color = ", delta)
