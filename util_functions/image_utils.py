import cv2

def find_overlap(rect:tuple[int,int,int,int],all_rect:list[tuple[int,int,int,int]]):
    if len(rect) != 4:
        return False
    
    x_1,y_1,w_1,h_1 = rect
    x_line_1 = (x_1,x_1 + w_1)
    y_line_1 = (y_1,y_1 + h_1)
    for (x,y,w,h) in all_rect:
        x_line_2 = (x,x + w)
        y_line_2 = (y,y + h)
        x_overlap = find_overlap_line(x_line_1,x_line_2)
        y_overlap = find_overlap_line(y_line_1,y_line_2)

        if  x_overlap and y_overlap:
            return True

def find_overlap_line(line_1:(int,int),line_2:(int,int)):
    if len(line_1) != 2 or len(line_2) != 2:
        return False
    start_1, end_1 = line_1
    start_2, end_2 = line_2

    # starts before
    if start_2 < start_1 and end_2 > start_1:
        return True

    # Starts inside other
    if start_2 >= start_1 and start_2 < end_1:
        return True
    
    # Starts after other
    return False
    

def resize_image(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)
