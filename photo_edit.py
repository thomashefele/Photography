#This is a hodgepodge of code right now because I do no have the time nor resources right now to make substantial headway on this project.
#Feel free to borrow code here or contact me w/ feedback.

import cv2
import numpy as np, argparse as ap
from tkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageDraw, ImageEnhance


resp, f_length, cropped, pil_temp = True, 1, None, None
f_type = [("JPG Images", "*.jpg"), ("PDF Files", "*.pdf"), ("PNG Images", "*.png"), ("Photoshop", "*.psd")]

def f_browse():
    global img_files, f_length, names
    names = []
    
    img_files = fd.askopenfilenames(initialdir= "/", title= "Select a File", filetypes= f_type)
    f_length = len(img_files)
    
    for i in range(f_length):
        names.append(img_files[i])
        
    sel_ph = StringVar()
    sel_ph.set("Choose photo")
    
    def show(event):
        photo = cv2.imread(sel_ph.get())
        cv2.imshow("Original", photo)
    
    drop = OptionMenu(main, sel_ph, *names, command= show)
    drop.grid(column= 2, row= 1)
    
def f_save(lib, tipo):
    s_length = len(save_imgs)
    
    if s_length == 0:
        return
    elif s_length == 1 and tipo == "":
        save_name = fd.asksaveasfilename(defaultextension= "*.jpg", filetypes= f_type, title= "Set filename")
        
        if lib == "cv2":
            cv2.imwrite(save_name, save_imgs[0])
        elif lib == "PIL":
            sig.save(save_name)
            sig_w.destroy()
    else:  
        for i in range(s_length):
            cv2.imwrite(img_files[i], save_imgs[i])
            
def stitcher():
    global save_imgs
    save_imgs = []
    imgs = []
    
    if f_length == 1:
        return
    
    for i in range(f_length):
        imgs.append(cv2.imread(img_files[i]))
        imgs[i] = cv2.resize(imgs[i],(0,0), fx= 0.4, fy= 0.4)
  
    st_image = cv2.Stitcher.create()
    (dummy, new_img) = st_image.stitch(imgs)
  
    if dummy != cv2.STITCHER_OK:
        print("Your Panorama isn't ready")
    else: 
        print("Your Panorama is ready!!!")
        
    save_imgs.append(new_img)
    cv2.imshow('test', new_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def edit():
    global cropped
    img = cv2.imread(img_files[0])
    cv2.imshow("test", img)
    
    def cropper(event, x, y, flags, params):
        img_cp = img.copy()
        
        if event == cv2.EVENT_LBUTTONDOWN:
            global x1, y1
            x1, y1 = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            global x2, y2
            x2, y2 = x, y
            image = cv2.rectangle(img_cp, (x1, y1), (x2, y2), 0, 8)
            cv2.imshow("test", image)

            if x2 > x1:
                if y2 > y1:
                    cropped = img[y1:y2, x1:x2]
                else:
                    cropped = img[y2:y1, x1:x2]
            elif x1 > x2:
                if y2 > y1:
                    cropped = img[y1:y2, x2:x1]
                else:
                    cropped = img[y2:y1, x2:x1]
            else:
                pass

            try:
                cv2.imshow("crop", cropped)
                cv2.waitKey(0)
                cv2.destroyWindow("crop")      
            except UnboundLocalError:
                pass
                
    cv2.setMouseCallback("test", cropper)
    color_rev = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_temp = Image.fromarray(color_rev)
    
    def contr(event):
        global contr_sc
        contr_sc = float(event)/50
        
    def color(event):
        global color_sc
        color_sc = float(event)/50
        
    def bright(event):
        global bright_sc
        bright_sc = float(event)/50
        
    def sharp(event):
        global sharp_sc
        sharp_sc = float(event)/50
        
    cv2.createTrackbar("Contrast", "r", 0, 100, contr)
    cv2.createTrackbar("Brightness", "r", 0, 100, bright)
    cv2.createTrackbar("Sharpness", "r", 0, 100, sharp)
    
    old_contr, old_color, old_bright, old_sharp = 0,0,0,0


def done_crop():
    cv2.destroyAllWindows()

def signature():
    global sig, draw, sig_w, save_imgs
    
    sig_w = Tk()
    cvs = Canvas(sig_w, width= 500, height= 200)
    cvs.pack()

    sig = Image.new('RGB', (500,200), (0,0,0))
    draw = ImageDraw.Draw(sig)

    clickety = False
    last = None

    def cliq(event):
        global clickety
        clickety = True

    def release(event):
        global clickety
        clickety = False

    cvs.bind_all('<ButtonPress-1>', cliq)
    cvs.bind_all('<ButtonRelease-1>', release)

    def move(event):
        global clickety 
        global last
        x,y = event.x,event.y

        if clickety:
            if last is None:
                last = (x,y)
                return

            draw.line(((x,y),last), (255,255,255), width= 7)
            cvs.create_line(x,y,last[0],last[1], smooth= True, width= 5)
            last = (x,y)
        else:
            last = (x,y)

    cvs.bind_all('<Motion>', move)
    save_imgs.append(sig)

    sig_save = Button(sig_w, text= "Save Signature", command= lambda: f_save("PIL"))
    sig_save.pack()

    sig_w.mainloop()
    
def wm_adder():
    global img_files
    global save_imgs
    
    save_imgs = []
    wm_file = fd.askopenfilename(initialdir= "/", title= "Select a Watermark Logo", filetypes= f_type)
    logo = cv2.imread(wm_file)
    
    h_logo, w_logo, _ = logo.shape
    
    for i in range(f_length):
        wm_img = cv2.imread(img_files[i])
        h_img, w_img, _ = wm_img.shape
        new_img = np.concatenate([wm_img, np.full((h_img, w_img, 0), 255, dtype= np.uint8)], axis= -1)

        center_y = int(0.03*h_img)
        center_x = int(0.95*w_img)

        top_y = center_y - int(h_logo/2)
        left_x = center_x - int(w_logo/2)
        bottom_y = top_y + h_logo
        right_x = left_x + w_logo

        destination = new_img[top_y:bottom_y, left_x:right_x]
        result = cv2.addWeighted(destination, 1, logo, 0.5, 0)

        new_img[top_y:bottom_y, left_x:right_x] = result
        cv2.imshow(f"test {i}", new_img)
        save_imgs.append(new_img)
        
    cv2.waitKey(0)
    cv2.destroyAllWindows()

main = Tk()
main.title("Photo Editor")
main.geometry("500x500")
main.config(background = "blue")
  
button_explore = Button(main, text= "Browse Files", command= f_browse)
button_stitch = Button(main, text= "Stitch", command= stitcher)
button_crop = Button(main, text= "Crop", command= edit)
button_done = Button(main, text= "Done Cropping", command= done_crop)
button_sig = Button(main, text= "Create signature", command= signature)
button_wm = Button(main, text= "Add watermark", command= wm_adder)
button_save = Button(main, text= "Save", command= lambda: f_save("cv2"))

button_explore.grid(column = 1, row = 1)
button_stitch.grid(column = 1, row = 2)
button_crop.grid(column = 1, row = 3)
button_done.grid(column = 1, row = 4)
button_sig.grid(column = 1, row = 5)
button_wm.grid(column = 1, row = 6)
button_save.grid(column = 1, row = 7)
  
main.mainloop()

import cv2

def BrightnessContrast(brightness=0):
	
	# getTrackbarPos returns the current
	# position of the specified trackbar.
	brightness = cv2.getTrackbarPos('Brightness',
									'GEEK')
	
	contrast = cv2.getTrackbarPos('Contrast',
								'GEEK')

	effect = controller(img, brightness,
						contrast)

	# The function imshow displays an image
	# in the specified window
	cv2.imshow('Effect', effect)

def controller(img, brightness=255,
			contrast=127):
	
	brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))

	contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))

	if brightness != 0:

		if brightness > 0:

			shadow = brightness

			max = 255

		else:

			shadow = 0
			max = 255 + brightness

		al_pha = (max - shadow) / 255
		ga_mma = shadow

		# The function addWeighted calculates
		# the weighted sum of two arrays
		cal = cv2.addWeighted(img, al_pha,
							img, 0, ga_mma)

	else:
		cal = img

	if contrast != 0:
		Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
		Gamma = 127 * (1 - Alpha)

		# The function addWeighted calculates
		# the weighted sum of two arrays
		cal = cv2.addWeighted(cal, Alpha,
							cal, 0, Gamma)

	# putText renders the specified text string in the image.
	cv2.putText(cal, 'B:{},C:{}'.format(brightness,
										contrast), (10, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

	return cal

if __name__ == '__main__':
	# The function imread loads an image
	# from the specified file and returns it.
	original = cv2.imread("/Users/thomashefele/Desktop/DSC_0094.JPG")

	# Making another copy of an image.
	img = original.copy()

	# The function namedWindow creates a
	# window that can be used as a placeholder
	# for images.
	cv2.namedWindow('GEEK')

	# The function imshow displays an
	# image in the specified window.
	cv2.imshow('GEEK', original)

	# createTrackbar(trackbarName,
	# windowName, value, count, onChange)
	# Brightness range -255 to 255
	cv2.createTrackbar('Brightness',
					'GEEK', 255, 2 * 255,
					BrightnessContrast)
	
	# Contrast range -127 to 127
	cv2.createTrackbar('Contrast', 'GEEK',
					127, 2 * 127,
					BrightnessContrast)

	
	BrightnessContrast(0)

# The function waitKey waits for
# a key event infinitely or for delay
# milliseconds, when it is positive.
cv2.waitKey(0)
