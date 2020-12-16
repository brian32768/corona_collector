//import "jquery"
import posRates from "./posrates"

import "./barline.css"

const title = "Clatsop County Daily"

const chart = "cases";
posRates(chart);

document.getElementById("app").innerHTML = title;

