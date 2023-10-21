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

def force_image_size(image, width=None, height=None, inter=cv2.INTER_AREA,fill_color=[0,0,0]):
    dim = None
    org_size_h_w = image.shape[:2] 
    org_size_w_h = org_size_h_w[1], org_size_h_w[0]

    if width is None and height is None:
        return image
    
    dim = resize_dimension(org_size_w_h,width,height)
    resized_image = cv2.resize(image, dim, interpolation=inter)

    if dim == (width,height):
        return resized_image
    else:
        img_w, img_h = dim
        w_extra = width - img_w
        top_extra = w_extra // 2
        bottom_extra = w_extra - top_extra

        h_extra = height - img_h
        left_extra = h_extra // 2
        right_extra = h_extra - left_extra

        border_image = cv2.copyMakeBorder(
            resized_image,
            top=top_extra,
            bottom=bottom_extra,
            left=left_extra,
            right=right_extra,
            borderType=cv2.BORDER_CONSTANT,
            value=fill_color
        )
        return border_image


def resize_image(image, max_width=None, max_height=None, inter=cv2.INTER_AREA):
    dim = None
    org_size_h_w = image.shape[:2] 
    org_size_w_h = org_size_h_w[1], org_size_h_w[0]

    if max_width is None and max_height is None:
        return image
    
    dim = resize_dimension(org_size_w_h,max_width,max_height)

    return cv2.resize(image, dim, interpolation=inter)

def resize_dimension(org_size_w_h,max_width=None, max_height=None) -> tuple[int,int]:
    (w, h) = org_size_w_h

    if max_width is None and max_height is None:
        return org_size_w_h
    
    if max_width is not None and max_height is not None:
        dim_w_w, dim_w_h = resize_dimension(org_size_w_h,max_width,None)
        dim_h_w, dim_h_h = resize_dimension(org_size_w_h,None,max_height)

        if dim_w_h > max_height:
            return (dim_h_w, dim_h_h)
        else:
            return (dim_w_w, dim_w_h)

    if max_width is None:
        r = max_height / float(h)
        return (int(w * r), max_height)
    else:
        r = max_width / float(w)
        return (max_width, int(h * r))