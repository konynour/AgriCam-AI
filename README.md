An open-source application for image processing and soil moisture calculation from photos of tomato plants

Piecewise linear regression with breakpoint prediction models to calculate soil moisture using tomato leaves color and soil temperature

+ First, it imports the necessary modules (libraries): OpenCV (cv2) to process images, urllib.request to retrieve an image from a URL, numpy for working with arrays and serial for serial communication with Arduino.
+ It then retrieves an image from a URL and stores it as a numpy array. OpenCV's cv2.imdecode() function is used to decode the image into a format that can be processed by OpenCV.
+ It then creates two binary masks for two regions of interest in the image (namely the young leaf regions only, the points of the polygons are set manually in a pre-calibration), using cv2.fillConvexPoly() to draw polygons (irregular quadrilaterals) around each region.
+ The program then uses cv2.bitwise_and() to apply the masks to the image, resulting in a masked image that shows only the two regions of interest.
+ A scaling factor is then calculated to resize the masked image, preparing it for the next step, rendering it to the screen, so that it is 1080 pixels tall, the normal resolution height of a modern monitor. Resizing the masked image is done using the cv2.resize() function.
+ The program displays the resized masked image using cv2.imshow(), waits for a key to be pressed using cv2.waitKey(), and writes the masked image locally using the cv2.imwrite() function.
+ It then calculates the number of non-zero pixels (just for information) in each mask using cv2.countNonZero() and the mean RGB color values for each region using cv2.mean().
+ Calculate the soil moisture value for the two rows based on their respective mean green color value using the non-linear model (3), which is the heart of the control law, thus acting as a regulator and controlling the actuator to start and stop irrigation.
+ Based on the calculations in Table 4, the Gavg color component was selected for soil moisture calculation and irrigation management,. This color component results in the smallest errors in soil moisture prediction (from -6% to 6% depending on whether Gavg has value greater or less than the breakpoint). Prediction errors are accounted for and corrected in the soil moisture calculation as well as the correction factor for the specific soil type (in this case resulting soil moisture readings must be multiplied by coefficient of 1.1).
+ Finally, the results of the soil moisture calculation and irrigation decision are printed for the user to view. Communication is also carried out with the Arduino board using the serial module, sending a message to start or stop irrigation in the two monitored rows of plantations, depending on the calculated soil moisture value.


Required libraries:

    OpenCV
    Numpy
    urllib.request
    serial


Author: Svetoslav Atanasov; 
e-mail: svetoslav.atanasov@trakia-uni.bg
