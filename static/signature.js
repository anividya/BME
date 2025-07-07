(function() {
    const sb = document.getElementById("btnSubmitSign"); // ✅ Fixed ID
    const canvasDataSTAT = document.getElementById("CanvasDataSTAT"); 
    const canvas = document.getElementById('myCanvas');
    const ctx = canvas.getContext('2d');
    let drawing = false;
    let dr = false;
    let firstdr = false;

    // Get the correct canvas position accounting for scaling
    function getCanvasPosition() {
        const rect = canvas.getBoundingClientRect();
        return {
            scaleX: canvas.width / rect.width,
            scaleY: canvas.height / rect.height
        };
    }

    function getCoords(event) {
        const pos = getCanvasPosition();
        let clientX, clientY;
        
        if (event.touches?.[0]) {
            clientX = event.touches[0].clientX;
            clientY = event.touches[0].clientY;
        } else {
            clientX = event.clientX;
            clientY = event.clientY;
        }
        
        const rect = canvas.getBoundingClientRect();
        return {
            x: (clientX - rect.left) * pos.scaleX,
            y: (clientY - rect.top) * pos.scaleY
        };
    }

    function startDrawing(e) {
        drawing = true;
        dr = true;
        sb.setAttribute("type", "button");

        if (!firstdr) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            firstdr = true;
        }
        const coords = getCoords(e);
        ctx.beginPath();
        ctx.moveTo(coords.x, coords.y);
        e.preventDefault();
    }

    function draw(e) {
        if (drawing) {
            const coords = getCoords(e);
            ctx.lineTo(coords.x, coords.y);
            ctx.stroke();
            e.preventDefault();
        }
    }

    function stopDrawing() {
        drawing = false;
    }

    // Event Listeners
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);

    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    canvas.addEventListener('touchcancel', stopDrawing);

    // Submit Signature
    window.fun_submit = function() {
        if (dr) {
            const canvasData = canvas.toDataURL();
            document.getElementById('canvas_data').value = canvasData;
            document.getElementById('page').innerHTML = `<img src="${canvasData}" alt="Signature" style="max-width: 100%; height: auto;" />`;
            firstdr = false;
            sb.setAttribute("type", "button");
            document.getElementById("CanvasDataSTAT").value = "Signed";
        } else {
            sb.setAttribute("type", "button");
            alert('Please sign and Click Submit Sign');
            document.getElementById("CanvasDataSTAT").value = "NotSigned";
        }
    };

    // Clear Canvas
    window.clearbtn = function() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById('page').innerHTML = '';
        document.getElementById('canvas_data').value = '';
        dr = false;
        sb.setAttribute("type", "button");
        firstdr = false;
        drawWatermark();
        document.getElementById("CanvasDataSTAT").value = "NotSigned";
    };

    // Watermark
    function drawWatermark() {
        ctx.font = "20px Arial";
        ctx.fillStyle = "lightgray";
        ctx.textAlign = "center";
        ctx.fillText("Please Sign Here", canvas.width / 2, canvas.height / 2);
    }

    // Initialize
    drawWatermark();
})();