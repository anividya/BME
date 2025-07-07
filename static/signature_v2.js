// Common variables
let drawing = false;
let dr = false;
let firstdr = false;
let sg_avail1 = false;
let sg_avail2 = false

// Helper function to get the coordinates (works for both mouse and touch)
function getCoords(event, canvas) {
    const rect = canvas.getBoundingClientRect();
    if (event.touches && event.touches[0]) {
        return {
            x: event.touches[0].clientX - rect.left,
            y: event.touches[0].clientY - rect.top
        };
    } else {
        return {
            x: event.offsetX,
            y: event.offsetY
        };
    }
}

// Start drawing (mouse or touch)
function startDrawing(e, canvas, ctx) {
    drawing = true;
    dr = true;
    const sb = document.getElementById("btnSubmitSign" + canvas.id.slice(-1));
    sb.setAttribute("type", "button");

    if (!firstdr) {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the watermark
        firstdr = true;
    }
    const coords = getCoords(e, canvas);
    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
    e.preventDefault(); // Prevent scrolling or unwanted gestures
}

// Continue drawing (mouse or touch)
function draw(e, canvas, ctx) {
    if (drawing) {
        const coords = getCoords(e, canvas);
        ctx.lineTo(coords.x, coords.y);
        ctx.stroke();
        e.preventDefault(); // Prevent scrolling or unwanted gestures
    }
}

// Stop drawing (mouse or touch)
function stopDrawing() {
    drawing = false;
}

// Add event listeners dynamically
function initializeCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    canvas.addEventListener('mousedown', (e) => startDrawing(e, canvas, ctx));
    canvas.addEventListener('mousemove', (e) => draw(e, canvas, ctx));
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);
    canvas.addEventListener('touchstart', (e) => startDrawing(e, canvas, ctx));
    canvas.addEventListener('touchmove', (e) => draw(e, canvas, ctx));
    canvas.addEventListener('touchend', stopDrawing);
    canvas.addEventListener('touchcancel', stopDrawing);

    // Draw the watermark
    drawWatermark(canvas, ctx);
}

// Function to submit the drawn signature
function fun_submit(canvasId, sbId, pageId, inputId) {
    const canvas = document.getElementById(canvasId);
    const sb = document.getElementById(sbId);
    const ctx = canvas.getContext('2d');
    console.log(canvasId);
    if (canvasId == 'myCanvas1') {
        sg_avail1 = true;
    }
    if (canvasId == 'myCanvas2') {
        sg_avail2 = true;
    }
    if (dr) {
        const canvasData = canvas.toDataURL(); // Get the data URL of the drawn image
        document.getElementById(inputId).value = canvasData; // Set it in the hidden input field
        document.getElementById(pageId).innerHTML = '<img src="' + canvasData + '" alt="Signature" style="max-width: 100%; height: auto;" />';
        firstdr = false;
        sb.setAttribute("type", "button");
    } else {
        sb.setAttribute("type", "button");
        alert('Please sign and Click Submit Sign');
    }
}

// Function to clear the canvas
function clearbtn(canvasId, sbId, pageId, inputId) {
    const canvas = document.getElementById(canvasId);
    const sb = document.getElementById(sbId);
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    document.getElementById(pageId).innerHTML = ''; // Clear the displayed image
    document.getElementById(inputId).value = ''; // Clear the hidden input field
    dr = false;
    if (canvasId == 'myCanvas1') {
        sg_avail1 = false;
    }
    if (canvasId == 'myCanvas2') {
        sg_avail2 = false;
    }
    sb.setAttribute("type", "button");
    firstdr = false;
    drawWatermark(canvas, ctx);
}

// Function to check if signature is present
function signcheck() {
    if (dr) {
        // Signature is present
    } else {
        alert('Please sign and Click Submit Sign');
    }
}

// Function to draw the watermark on the canvas
function drawWatermark(canvas, ctx) {
    ctx.font = "20px Arial";
    ctx.fillStyle = "lightgray";
    ctx.textAlign = "center";
    ctx.fillText("Please Sign Here", canvas.width / 2, canvas.height / 2);
}

// Initialize all canvases on page load
document.addEventListener("DOMContentLoaded", function () {
    initializeCanvas('myCanvas1');
    initializeCanvas('myCanvas2');
});

function form_submit(bt_id) {

    const sbtn = document.getElementById(bt_id);

    if (dr) {
        if (sg_avail1 == true && sg_avail2 == true) {
            sbtn.setAttribute("type", "submit");
        }
        else {
            alert('Please sign and Click Submit Sign');
        }

    } else {
        alert('Please sign and Click Submit Sign');
    }

}