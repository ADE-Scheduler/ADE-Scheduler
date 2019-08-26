
function processHEX(val) {
    let hex = (val.length > 6)?val.substr(1, val.length - 1):val;

    let r, g, b;
    if (hex.length > 3) {
        r = hex.substr(0, 2);
        g = hex.substr(2, 2);
        b = hex.substr(4, 2);
    } else {
        r = hex.substr(0, 1) + hex.substr(0, 1);
        g = hex.substr(1, 1) + hex.substr(1, 1);
        b = hex.substr(2, 1) + hex.substr(2, 1);
    }

    return [
        parseInt(r, 16),
        parseInt(g, 16),
        parseInt(b, 16)
    ]
}

function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function getGradient(hex1, hex2, steps) {

    let color1RGB = processHEX(hex1);
    let color2RGB = processHEX(hex2);
    let colors = [];
    let stepsPerc = 100 / (steps + 1);
    let valDiffRGB = [
        color2RGB[0] - color1RGB[0],
        color2RGB[1] - color1RGB[1],
        color2RGB[2] - color1RGB[2]
    ];

    // build the color array out with color steps
    for (let i = 0; i < steps; i++) {
        let clampedR = (valDiffRGB[0] > 0)
        ? pad((Math.round(valDiffRGB[0] / 100 * (stepsPerc * (i + 1)))).toString(16), 2)
        : pad((Math.round((color1RGB[0] + (valDiffRGB[0]) / 100 * (stepsPerc * (i + 1))))).toString(16), 2);

        let clampedG = (valDiffRGB[1] > 0)
        ? pad((Math.round(valDiffRGB[1] / 100 * (stepsPerc * (i + 1)))).toString(16), 2)
        : pad((Math.round((color1RGB[1] + (valDiffRGB[1]) / 100 * (stepsPerc * (i + 1))))).toString(16), 2);

        let clampedB = (valDiffRGB[2] > 0)
        ? pad((Math.round(valDiffRGB[2] / 100 * (stepsPerc * (i + 1)))).toString(16), 2)
        : pad((Math.round((color1RGB[2] + (valDiffRGB[2]) / 100 * (stepsPerc * (i + 1))))).toString(16), 2);

        let textColor = ((r*299)+(g*587)+(b*114))/1000 > 127.5 ? 'white' : 'black';
        let hexColor = ['#', clampedR, clampedG, clampedB].join('');

        colors[i] = [hexColor, textColor];
    }
    return colors
}