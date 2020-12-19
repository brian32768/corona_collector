import posRates from './posrates';
import "./barline.css"

const title = "Clatsop County Daily"

posRates('cases');
document.getElementById("app").innerHTML = title;

