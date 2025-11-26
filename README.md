# Restaurant Food Recognition for Calorie Estimation Project

## Overview
This project implements a **Convolutional Neural Network (CNN)** to classify food images from the **Food-101 dataset** into 101 distinct categories such as pizza, pasta, sushi, burger, etc.  
The model is built using **Pytorch** and deployed as a **REST API** for prediction. Then the frontend UI fetches the relevant nutrition facts from a predefined JavaScript object

## Project Structure
```
Food_Classification/
│
├── data/
│   ├── food-101                   # Add downloaded images into this folder.             
│      
├── api/
│   ├── app.py                     # Flask backend
│   ├── bestfood101_res50.pth      # Trained model
│   ├── food101_class_names.json   # food 101 classification
│   ├── model_service.py           # Prediction logic 
│
├── model/
│   └── model_training.py          # Model training
│
├── ui/
│   ├── index.html                 # HTML
│   ├── script.js                  # JavaScript, has the food items with corresponding calorie values
│   ├── style.css                  # CSS
│
├── requirements.txt               # all dependencies of this project are listed here.
└── README.md                      # README file
└── Group_29_DL_Project_Report.pdf # a report highlighting contributions and main results.
```

---

Extract group_29.zip

Open folder from visual studio code

Download and extract the dataset using:
```bash
wget http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz
tar -xvzf food-101.tar.gz
```
Save it in data\food-101 for model training.

---

## Model Building & Testing

### 1 Install dependencies
Open terminal in visual studio code using project environment (python.exe) and run all below commands. Make sure python >= v3.9 in your system.
[View --> Command Palette.. -> Python: Create environment -> select Venv -> select requirement.txt file (for virtual environment set)]

```bash
pip install -r requirements.txt
```

### 2 Build and train the model
You can run below commands for trained model testing.

```bash
cd model
python build_model.py
```
After completion of build, it will create model. Ex: bestfood101_res50.pth

## API Setup (inference)

### 1 Install required libraries
```bash
pip install -r .\requirements.txt
```

### 2
 Run the API
```bash
CD api
python app.py
```

### 3 Test API with curl (used tool: Postman)
```bash
curl -X POST "http://127.0.0.1:5000/predict"      -F "file=@Burger.jpg"
```

### 4 UI
open folder name: "ui" and open "index.html" file in browser.

Now, upload sample food image by click on "Choose file" option in UI.
Next click on "Deep Learning Prediction" button for food recognition and calorie estimation.
---

## Example Output
```json
{
  "prediction": [
    {
      "class": "hamburger",
      "probability": 77.0
    }]
}
```

For more details and clarity in installation, please contact:
M24AID031@iitj.ac.in
M24AID009@iitj.ac.in
M24AID028@iitj.ac.in
M24AID024@iitj.ac.in

--- `From image to ingredient, from bytes to bites — decoding food, one pixel at a time.`