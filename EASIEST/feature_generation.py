def screen_find_element(cordinates, oran, current_file):
    try:
        file_string = "EASIEST/files/" + current_file + ".txt"
        with open(file_string, "r") as file:  # reading the files for segmentation coordinates
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            splited_strings = line.split(" ")
            # dynamically computing the adjusted (for each screen) segmentation elements coordinates
            x1 = float(splited_strings[0]) * oran
            y1 = float(splited_strings[2]) * oran
            x2 = (float(splited_strings[0]) + float(splited_strings[1])) * oran
            y2 = (float(splited_strings[2]) + float(splited_strings[3])) * oran
            # determining the screen element which the X, Y value inside
            if x1 <= cordinates[0] <= x2 and y1 <= cordinates[1] <= y2:
                return splited_strings[4]  # returning the element


    except IOError as error:
        print(error)


def compute_metrics(data_eye_track, current_file):  # data_eye_track = ["ID", "X", "Y", "First Time", "Duration","Total Fixation Count", "Element"], ...
                                                    # current_file = WEB PAGE NAME !!
    try:
        file_string = "EASIEST/files/" + current_file + ".txt"  # segmentation files that Yeliz Yeşilada provided
        with open(file_string, "r") as file:
            lines = file.readlines()  # each line in segmentation .txt ; for example "955 164 18 36 A"

        all_elements = {}  # empty dictionary
        for line in lines:
            line = line.strip()
            element = line.split(" ")[4]  # acquiring the element name which is 4th index (A,B,C,..)

            all_elements[element] = 0  # I created a dictionary key-value pair for each segmentation element for each web-page !!
            # I started all from 0 because

        features = {}  # empty dictionary again

        for eye_values in data_eye_track:  # eye-values : ["ID", "X", "Y", "First Time", "Duration","Total Fixation Count", "Element"]

            element = eye_values[6]  # ELEMENT value of IVT applied gaze-points
            fixation_counts = eye_values[5]  # TOTAL FIXATION COUNT of IVT applied gaze-points
            all_elements[element] = 1  # updating my all_elements dictionary (marked as seen)
            duration = float(eye_values[4])  # DURATION VALUE (will use it for % total) of IVT applied gaze-points
            first_time_look = float(eye_values[3])  # FIRST TIME LOOK of IVT applied gaze-points

            global prev  # global variable defined for feature generation

            if element in features:  # means, if this element is already defined in my feature dictionary, so I can add up my duration .. etc. varabiles onto it.
                features[element][0] += duration  # total duration appending
                features[element][3] += fixation_counts  # total fixation counts appending
                if prev != element:  # this is just determining the revisit count
                    features[element][2] += 1  # if previous element is not equal to current element then previous count increased
                prev = element  # updating the prev element for next comparison
            elif element is None:
                pass  # if patient looked non-valid parts of the web-site page, I just do nothing
            else:  # this else part is for creating the features dictionary for THE FIRST TIME ELEMENT LOOKED !!!
                features[element] = []
                features[element].append(duration)
                features[element].append(first_time_look)
                # revisits
                features[element].append(1)
                features[element].append(fixation_counts)
                prev = element

        for element in all_elements.keys():  # If there are elements on the website that the patient has never looked at, I have taken the necessary steps for the .csv file.
            if all_elements[element] == 0:
                pass
                # features[element] = []
                # features[element].append(0)
                # features[element].append(-1)
                # features[element].append(0)
                # features[element].append(0)

        return features  # returning the features dictionary to app.py (/save_data)


    except IOError as error:
        print(error)



def grid_find_element(cordinates, oran):
    if 0 <= cordinates[0] <= (1280*oran)/3 and 0 <= cordinates[1] <= (1024*oran)/3:
        return "A"
    elif (1280*oran)/3 <= cordinates[0] <= (1280*2*oran)/3 and 0 <= cordinates[1] <= (1024*oran)/3:
        return "B"
    elif (1280*2*oran)/3  <= cordinates[0] <= (1280*oran) and 0 <= cordinates[1] <= (1024*oran)/3:
        return "C"

    elif 0  <= cordinates[0] <= (1280*oran)/3 and (1024*oran)/3 <= cordinates[1] <= (1024*2*oran)/3:
        return "D"
    elif (1280 * oran) / 3 <= cordinates[0] <= (1280 * 2 * oran) / 3 and (1024 * oran) / 3 <= cordinates[1] <= (1024 * 2 * oran) / 3:
        return "E"
    elif (1280 * 2 * oran) / 3 <= cordinates[0] <= (1280 * oran) and (1024 * oran) / 3 <= cordinates[1] <= (1024 * 2 * oran) / 3:
        return "F"

    elif 0 <= cordinates[0] <= (1280*oran)/3 and (1024*2*oran)/3 <= cordinates[1] <= (1024*oran):
        return "G"
    elif (1280 * oran) / 3 <= cordinates[0] <= (1280 * 2 * oran) / 3 and (1024*2*oran)/3 <= cordinates[1] <= (1024*oran):
        return "H"
    elif (1280 * 2 * oran) / 3 <= cordinates[0] <= (1280 * oran) and (1024*2*oran)/3 <= cordinates[1] <= (1024*oran):
        return "I"
