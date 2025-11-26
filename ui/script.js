$(document).ready(function () {
  let selectedFile;
  let nutritionData;

  $("#imageInput").on("change", function (e) {
    selectedFile = e.target.files[0];
    if (selectedFile) {
      $("#preview").css("display", "block");
      $("#preview").attr("src", URL.createObjectURL(selectedFile));
    }
  });

  $("#predictBtn").click(function () {
    if (!selectedFile) {
      alert("Please select an image first!");
      return;
    }

    let formData = new FormData();
    formData.append("image", selectedFile);

    $("#result").text("Processing...");
    
    $.ajax({
      url: "http://localhost:5000/predict", // Flask or Node backend
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (data) {
        $("#result").text("Image Testing Completed..");
        if(data["prediction"].length > 0 && data["prediction"][0].probability > 50){
          $("#foodName span").text(data["prediction"][0].class);
          $("#probability span").text(data["prediction"][0].probability + "%");
          $("#calories").text(nutritionData[data["prediction"][0].class].Calories + " kcal/100g");
          $("#fat").text(nutritionData[data["prediction"][0].class].Fat);
          $("#protein").text(nutritionData[data["prediction"][0].class].Protein);
          $("#carbs").text(nutritionData[data["prediction"][0].class].Carbohydrate);
        }
        else{
          let naName = "NA";
          $("#foodName span").text(naName);
          $("#probability span").text(naName);
          $("#calories").text(naName);
          $("#fat").text(naName);
          $("#protein").text(naName);
          $("#carbs").text(naName);
        }
      },
      error: function () {
        alert("Error contacting server.");
      }
    });
  });

  nutritionData = {
  "apple_pie": {"Calories": 300, "Fat": 14, "Protein": 3, "Carbohydrate": 42},
  "baby_back_ribs": {"Calories": 430, "Fat": 35, "Protein": 28, "Carbohydrate": 5},
  "baklava": {"Calories": 330, "Fat": 22, "Protein": 4, "Carbohydrate": 32},
  "beef_carpaccio": {"Calories": 200, "Fat": 12, "Protein": 20, "Carbohydrate": 0},
  "beef_tartare": {"Calories": 220, "Fat": 15, "Protein": 22, "Carbohydrate": 1},
  "beet_salad": {"Calories": 150, "Fat": 6, "Protein": 3, "Carbohydrate": 18},
  "beignets": {"Calories": 250, "Fat": 14, "Protein": 3, "Carbohydrate": 28},
  "bibimbap": {"Calories": 560, "Fat": 18, "Protein": 20, "Carbohydrate": 75},
  "bread_pudding": {"Calories": 290, "Fat": 9, "Protein": 6, "Carbohydrate": 48},
  "breakfast_burrito": {"Calories": 350, "Fat": 19, "Protein": 14, "Carbohydrate": 30},
  "bruschetta": {"Calories": 190, "Fat": 7, "Protein": 4, "Carbohydrate": 25},
  "caesar_salad": {"Calories": 220, "Fat": 14, "Protein": 8, "Carbohydrate": 10},
  "cannoli": {"Calories": 250, "Fat": 15, "Protein": 5, "Carbohydrate": 28},
  "caprese_salad": {"Calories": 180, "Fat": 12, "Protein": 8, "Carbohydrate": 8},
  "carrot_cake": {"Calories": 350, "Fat": 16, "Protein": 5, "Carbohydrate": 45},
  "ceviche": {"Calories": 160, "Fat": 4, "Protein": 22, "Carbohydrate": 8},
  "cheesecake": {"Calories": 420, "Fat": 28, "Protein": 6, "Carbohydrate": 36},
  "cheese_plate": {"Calories": 400, "Fat": 33, "Protein": 25, "Carbohydrate": 3},
  "chicken_curry": {"Calories": 280, "Fat": 16, "Protein": 26, "Carbohydrate": 8},
  "chicken_quesadilla": {"Calories": 350, "Fat": 18, "Protein": 22, "Carbohydrate": 26},
  "chicken_wings": {"Calories": 375, "Fat": 27, "Protein": 32, "Carbohydrate": 3},
  "chocolate_cake": {"Calories": 390, "Fat": 16, "Protein": 6, "Carbohydrate": 55},
  "chocolate_mousse": {"Calories": 340, "Fat": 24, "Protein": 5, "Carbohydrate": 30},
  "churros": {"Calories": 290, "Fat": 15, "Protein": 3, "Carbohydrate": 36},
  "clam_chowder": {"Calories": 250, "Fat": 10, "Protein": 15, "Carbohydrate": 24},
  "club_sandwich": {"Calories": 420, "Fat": 22, "Protein": 28, "Carbohydrate": 35},
  "crab_cakes": {"Calories": 310, "Fat": 20, "Protein": 22, "Carbohydrate": 10},
  "creme_brulee": {"Calories": 320, "Fat": 24, "Protein": 6, "Carbohydrate": 25},
  "croque_madame": {"Calories": 420, "Fat": 26, "Protein": 24, "Carbohydrate": 25},
  "cup_cakes": {"Calories": 280, "Fat": 12, "Protein": 3, "Carbohydrate": 38},
  "deviled_eggs": {"Calories": 130, "Fat": 10, "Protein": 6, "Carbohydrate": 1},
  "donuts": {"Calories": 270, "Fat": 15, "Protein": 3, "Carbohydrate": 30},
  "dumplings": {"Calories": 210, "Fat": 8, "Protein": 10, "Carbohydrate": 25},
  "edamame": {"Calories": 190, "Fat": 8, "Protein": 17, "Carbohydrate": 14},
  "eggs_benedict": {"Calories": 320, "Fat": 22, "Protein": 16, "Carbohydrate": 18},
  "escargots": {"Calories": 220, "Fat": 17, "Protein": 18, "Carbohydrate": 2},
  "falafel": {"Calories": 330, "Fat": 18, "Protein": 13, "Carbohydrate": 30},
  "filet_mignon": {"Calories": 300, "Fat": 20, "Protein": 28, "Carbohydrate": 0},
  "fish_and_chips": {"Calories": 600, "Fat": 30, "Protein": 35, "Carbohydrate": 50},
  "foie_gras": {"Calories": 430, "Fat": 40, "Protein": 10, "Carbohydrate": 3},
  "french_fries": {"Calories": 365, "Fat": 17, "Protein": 5, "Carbohydrate": 48},
  "french_onion_soup": {"Calories": 250, "Fat": 12, "Protein": 9, "Carbohydrate": 20},
  "french_toast": {"Calories": 290, "Fat": 12, "Protein": 9, "Carbohydrate": 34},
  "fried_calamari": {"Calories": 350, "Fat": 20, "Protein": 18, "Carbohydrate": 25},
  "fried_rice": {"Calories": 380, "Fat": 12, "Protein": 8, "Carbohydrate": 55},
  "frozen_yogurt": {"Calories": 220, "Fat": 4, "Protein": 6, "Carbohydrate": 40},
  "garlic_bread": {"Calories": 240, "Fat": 10, "Protein": 6, "Carbohydrate": 32},
  "gnocchi": {"Calories": 320, "Fat": 7, "Protein": 9, "Carbohydrate": 55},
  "greek_salad": {"Calories": 210, "Fat": 14, "Protein": 6, "Carbohydrate": 12},
  "grilled_cheese_sandwich": {"Calories": 370, "Fat": 24, "Protein": 14, "Carbohydrate": 28},
  "grilled_salmon": {"Calories": 350, "Fat": 22, "Protein": 34, "Carbohydrate": 0},
  "guacamole": {"Calories": 250, "Fat": 22, "Protein": 3, "Carbohydrate": 12},
  "gyoza": {"Calories": 200, "Fat": 9, "Protein": 9, "Carbohydrate": 22},
  "hamburger": {"Calories": 420, "Fat": 24, "Protein": 26, "Carbohydrate": 32},
  "hot_and_sour_soup": {"Calories": 110, "Fat": 4, "Protein": 7, "Carbohydrate": 10},
  "hot_dog": {"Calories": 310, "Fat": 18, "Protein": 11, "Carbohydrate": 27},
  "huevos_rancheros": {"Calories": 280, "Fat": 16, "Protein": 12, "Carbohydrate": 20},
  "hummus": {"Calories": 230, "Fat": 18, "Protein": 6, "Carbohydrate": 12},
  "ice_cream": {"Calories": 270, "Fat": 15, "Protein": 4, "Carbohydrate": 30},
  "lasagna": {"Calories": 360, "Fat": 18, "Protein": 20, "Carbohydrate": 28},
  "lobster_bisque": {"Calories": 260, "Fat": 18, "Protein": 12, "Carbohydrate": 10},
  "lobster_roll_sandwich": {"Calories": 370, "Fat": 22, "Protein": 20, "Carbohydrate": 26},
  "macaroni_and_cheese": {"Calories": 400, "Fat": 22, "Protein": 14, "Carbohydrate": 38},
  "macarons": {"Calories": 250, "Fat": 12, "Protein": 5, "Carbohydrate": 28},
  "miso_soup": {"Calories": 90, "Fat": 3, "Protein": 6, "Carbohydrate": 8},
  "mussels": {"Calories": 190, "Fat": 6, "Protein": 20, "Carbohydrate": 10},
  "nachos": {"Calories": 420, "Fat": 24, "Protein": 10, "Carbohydrate": 40},
  "omelette": {"Calories": 220, "Fat": 16, "Protein": 14, "Carbohydrate": 2},
  "onion_rings": {"Calories": 410, "Fat": 22, "Protein": 4, "Carbohydrate": 46},
  "oysters": {"Calories": 180, "Fat": 6, "Protein": 18, "Carbohydrate": 8},
  "pad_thai": {"Calories": 410, "Fat": 14, "Protein": 18, "Carbohydrate": 55},
  "paella": {"Calories": 430, "Fat": 14, "Protein": 22, "Carbohydrate": 54},
  "pancakes": {"Calories": 320, "Fat": 10, "Protein": 8, "Carbohydrate": 45},
  "panna_cotta": {"Calories": 340, "Fat": 24, "Protein": 5, "Carbohydrate": 28},
  "peking_duck": {"Calories": 380, "Fat": 24, "Protein": 28, "Carbohydrate": 10},
  "pho": {"Calories": 360, "Fat": 10, "Protein": 25, "Carbohydrate": 40},
  "pizza": {"Calories": 285, "Fat": 10, "Protein": 12, "Carbohydrate": 36},
  "pork_chop": {"Calories": 330, "Fat": 20, "Protein": 30, "Carbohydrate": 0},
  "poutine": {"Calories": 520, "Fat": 30, "Protein": 18, "Carbohydrate": 48},
  "prime_rib": {"Calories": 400, "Fat": 30, "Protein": 32, "Carbohydrate": 0},
  "pulled_pork_sandwich": {"Calories": 440, "Fat": 22, "Protein": 28, "Carbohydrate": 35},
  "ramen": {"Calories": 450, "Fat": 18, "Protein": 16, "Carbohydrate": 55},
  "ravioli": {"Calories": 330, "Fat": 12, "Protein": 14, "Carbohydrate": 42},
  "red_velvet_cake": {"Calories": 380, "Fat": 17, "Protein": 5, "Carbohydrate": 50},
  "risotto": {"Calories": 360, "Fat": 14, "Protein": 9, "Carbohydrate": 48},
  "samosa": {"Calories": 260, "Fat": 14, "Protein": 6, "Carbohydrate": 28},
  "sashimi": {"Calories": 180, "Fat": 8, "Protein": 24, "Carbohydrate": 0},
  "scallops": {"Calories": 220, "Fat": 8, "Protein": 22, "Carbohydrate": 10},
  "seaweed_salad": {"Calories": 150, "Fat": 8, "Protein": 4, "Carbohydrate": 14},
  "shrimp_and_grits": {"Calories": 410, "Fat": 22, "Protein": 22, "Carbohydrate": 32},
  "spaghetti_bolognese": {"Calories": 420, "Fat": 15, "Protein": 22, "Carbohydrate": 55},
  "spaghetti_carbonara": {"Calories": 460, "Fat": 22, "Protein": 18, "Carbohydrate": 48},
  "spring_rolls": {"Calories": 200, "Fat": 8, "Protein": 6, "Carbohydrate": 24},
  "steak": {"Calories": 370, "Fat": 24, "Protein": 33, "Carbohydrate": 0},
  "strawberry_shortcake": {"Calories": 320, "Fat": 14, "Protein": 5, "Carbohydrate": 42},
  "sushi": {"Calories": 310, "Fat": 8, "Protein": 14, "Carbohydrate": 45},
  "tacos": {"Calories": 310, "Fat": 16, "Protein": 18, "Carbohydrate": 25},
  "takoyaki": {"Calories": 350, "Fat": 18, "Protein": 10, "Carbohydrate": 34},
  "tiramisu": {"Calories": 420, "Fat": 26, "Protein": 6, "Carbohydrate": 40},
  "tuna_tartare": {"Calories": 210, "Fat": 8, "Protein": 22, "Carbohydrate": 4},
  "waffles": {"Calories": 310, "Fat": 12, "Protein": 7, "Carbohydrate": 42}
}

});
