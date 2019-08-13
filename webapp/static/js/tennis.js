        var canvas = document.getElementById("myCanvas");
        var ctx = canvas.getContext("2d");

        var x = canvas.width/2;
        var y = canvas.height-30;

        var ballRadius = 10;

        var dx = 2;
        var dy = -2;

        var paddleHeight = 100;
        var paddleWidth = 20;

        var paddleX1 = canvas.width/20;
        var paddleY1 = canvas.height/2;
        var paddleX2 = canvas.width - canvas.width/20 - paddleWidth;
        var paddleY2 = canvas.height/2;

        var oldY1 = paddleY1;
        var oldY2 = paddleY2;

        var score1 = 0;
        var score2 = 0;
        const maxScore = 5;

        var upPressed = false;
        var downPressed = false;
        var zPressed = false;
        var sPressed = false;
        document.addEventListener("keydown", keyDownHandler, false);
        document.addEventListener("keyup", keyUpHandler, false);

        function keyDownHandler(e) {
            if(e.key == "Up" || e.key == "ArrowUp") {
                upPressed = true;
            }
            else if(e.key == "Down" || e.key == "ArrowDown") {
                downPressed = true;
            }

            if(e.key == "z") {
                zPressed = true;
            }
            else if(e.key == "s") {
                sPressed = true;
            }

        }

        function keyUpHandler(e) {
            if(e.key == "Up" || e.key == "ArrowUp") {
                upPressed = false;
            }
            else if(e.key == "Down" || e.key == "ArrowDown") {
                downPressed = false;
            }

            if(e.key == "z") {
                zPressed = false;
            }
            else if(e.key == "s") {
                sPressed = false;
            }
        }

        function drawScores() {
            ctx.font = "16px Arial";
            ctx.fillStyle = "#0095DD";
            ctx.fillText("Score player 1: "+score1 + "\n" + "Score player2: "+score2, 8, 20);
        }

        function drawBall() {
            ctx.beginPath();
            ctx.arc(x, y, ballRadius, 0, Math.PI*2);
            ctx.fillStyle = "#0095DD";
            ctx.fill();
            ctx.closePath();
        }

        function drawPaddles() {
            ctx.beginPath();
            ctx.rect(paddleX1, paddleY1, paddleWidth, paddleHeight);
            ctx.fillStyle = "#0095DD";
            ctx.fill();
            ctx.closePath();

            ctx.beginPath();
            ctx.rect(paddleX2, paddleY2, paddleWidth, paddleHeight);
            ctx.fillStyle = "#0095DD";
            ctx.fill();
            ctx.closePath();
        }

        function draw() {
        // drawing code
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawBall();

            if(y + dy > canvas.height-ballRadius || y + dy < ballRadius) {
                dy = -dy;
            }

            // Left player (player2) collision
            if(x + dx < paddleX1 + ballRadius && y > paddleY1 && y < paddleY1 + paddleHeight) {
                dx = -dx;
                dx += 0.2*Math.sign(dx);
                dy += Math.sign(paddleY2 - oldY2) * 1;
            }

            // Left player (player2) out
            if(x + dx < ballRadius) {
                score1++;
                if(score1 == maxScore) {
                    alert("GAME OVER, Player1 won!");
                    document.location.reload();
                }
                else {
                    x = canvas.width/2;
                    y = canvas.height-30;
                    dx = 2;
                    dy = -2;
                }
            }

            // Right player (player1) collision
            if(x + dx > paddleX2 && y > paddleY2 && y < paddleY2 + paddleHeight) {
                dx = -dx;
                dx += 0.2*Math.sign(dx);
                dy += Math.sign(paddleY1 - oldY1) * 1;
            }

            // Right player (player1) out
            if(x + dx > canvas.width-ballRadius) {
                score2++;
                if(score2 == maxScore) {
                    alert("GAME OVER, Player2 won!");
                    document.location.reload();
                }
                else {
                    x = canvas.width/2;
                    y = canvas.height-30;
                    dx = 2;
                    dy = -2;
                }
            }

            x += dx;
            y += dy;

            if(upPressed && paddleY2 > 0) {
                oldY2 = paddleY2;
                paddleY2 -= 7;
            }
            else if(downPressed && paddleY2 < canvas.height - paddleHeight) {
                oldY2 = paddleY2;
                paddleY2 += 7;
            }

            if(zPressed && paddleY1 > 0) {
                oldY1 = paddleY1;
                paddleY1 -= 7;
            }
            else if(sPressed && paddleY1 < canvas.height - paddleHeight) {
                oldY1 = paddleY1;
                paddleY1 += 7;
            }
            drawPaddles();
            drawScores();

            requestAnimationFrame(draw);
        }

        // Draw
        draw();