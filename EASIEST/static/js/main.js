// Define an array to store eye tracking data
let eyeTrackingData = [];
window.onload = async function() {
    // Variable to track if recording eye tracking data is active
    let isRecording = false;
    //start the webGazer tracker
    await webgazer.setRegression('ridge') /* currently must set regression and tracker */
        .setGazeListener(function(data, clock) {
            // When gaze data is available and valid
            if (data && data.x !== null && data.y !== null) {
                if (!isRecording)
                {
                    isRecording = true;
                }
                // To keep track x, y, and clock values and also current test id (apple, avg..)
                eyeTrackingData.push([data.x, data.y, clock, window.testID]);
            } else {
                isRecording = false;
            }
        })
        .saveDataAcrossSessions(true)
        .begin();
        webgazer.showVideoPreview(false) /* we don't show the video preview */
            .showPredictionPoints(true) /* shows a square every 100 milliseconds where current prediction is */
            .applyKalmanFilter(true); /* Kalman Filter defaults to on. Can be toggled by user. */


    var setup = function() {
        // Set up the main canvas. The main canvas is used to calibrate the webgazer.
        var canvas = document.getElementById("plotting_canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        canvas.style.position = 'fixed';
        // it makes the canvas invisible
        canvas.style.visibility = 'hidden';
    };

    setup();

};

// when next button is clicked
document.getElementById('bottom-right-btn').addEventListener('click', function() {
    // We can access it with window variable, we assigned the values into local variables
    // decreasing ratio, testID, width padding, and user id
    let azalmaOrani = window.azalma_orani;
    let testID = window.testID;
    let widthRatio = window.widthRatio;
    const id = document.getElementById('testImage').getAttribute('data-id');


    //we make a POST request to process the data
        fetch('/save_data', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ eyeTrackingData, azalmaOrani ,widthRatio, testID, id})
        })
        .then(response => {
            if (response.ok) {
                console.log("data has been successfully saved.");
            } else {
                console.error("Failed to save data.");
            }
        })
        .catch(error => {
            console.error("An error occurred while saving CSV data:", error);
        });


        //we make a POST request to process modal 2
        fetch('/grid_data', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ eyeTrackingData, azalmaOrani ,widthRatio, testID, id})
        })
        .then(response => {
            if (response.ok) {
                console.log("data has been successfully saved.");
            } else {
                console.error("Failed to save data.");
            }
        })
        .catch(error => {
            console.error("An error occurred while saving CSV data:", error);
        });

});


// Set to true if you want to save the data even if you reload the page.
window.saveDataAcrossSessions = true;

window.onbeforeunload = function() {
    webgazer.end();
}

/**
 * Restart the calibration process by clearing the local storage and reseting the calibration point
 */
function Restart(){
    document.getElementById("Accuracy").innerHTML = "<a>Not yet Calibrated</a>";
    webgazer.clearData();
    ClearCalibration();
    PopUpInstruction();
}
