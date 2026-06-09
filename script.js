console.log("Bearing Capacity AI App Loaded");

// Button loading animation
document.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", () => {
        btn.innerText = "Processing...";
    });
});

// Form validation for prediction
function validateForm() {
    const phi = document.querySelector("input[name='phi']").value;
    const fos = document.querySelector("input[name='fos']").value;

    if (phi < 0 || phi > 45) {
        alert("Angle of friction must be between 0° and 45°");
        return false;
    }

    if (fos < 2 || fos > 5) {
        alert("Factor of Safety should be between 2 and 5");
        return false;
    }

    return true;
}