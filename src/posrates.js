import $ from 'jquery';
import * as d3 from 'd3';

var statewid = $("#cases").width();
    
var state_margin = {top: 40, right: 25, bottom: 20, left: 30},
    state_width = statewid - state_margin.left - state_margin.right,
    state_height = state_width*.6 - state_margin.top - state_margin.bottom;

var parseDate = d3.timeParse("%m/%d/%y");
var formatDate = d3.timeFormat("%B %e");
var formatClass = d3.timeFormat("%B%d");

    var xState = d3.scaleTime()
        .range([10, state_width-10]);
    
    var yState = d3.scaleLinear()
        .range([state_height, 0]);
        

function make_y_gridlines() {		
    return d3.axisLeft(yState)
        .ticks(3)
}



function addCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

export default function posRates(chart) {
    
    var colorlist = { 'rates': { 'bar': '#c6dbef', 'line': '#084594', 'hover': '#4292c6', 'end': '#2171b5' },'cases': { 'bar': '#fcc5c0', 'line': '#7a0177', 'hover': '#dd3497', 'end': '#ae017e' },'deaths': { 'bar': '#ccc', 'line': '#333', 'hover': '#999', 'end': '#666' }};
    
    var ticker = { 'rates': '.0%', 'cases': ',', 'deaths': ','};
    var note_pos = { 'rates': 0.08, 'cases': 200 };

    var line = d3.line()
        .curve(d3.curveMonotoneX)
        .defined(function(d) { return !isNaN(d.avg); })
        .x(function(d) { return xState(d.date); })
        .y(function(d) { return yState(d.avg); });
    
    const url = "./emd_total_cases.csv"
    d3.csv(url, (error, data) => {
            data.forEach( (d) => {
                    console.log(d);
                    d.avg = 10;
                    d[chart] = +d[chart];
                    if (d.avg == 0) {
                        d.avg = 'null';
                    } else {
                        d.avg = +d.avg;
                    }
                    d.date = parseDate(d.date);
                });

            xState.domain(d3.extent(data, function (d) { return d.date; }));
            yState.domain([0, d3.max(data, function (d) { return d[chart]; })]);

            var rectwidth = (state_width / data.length) - .5;
            var halfway = (data.length / 4).toFixed();

            var svg4 = d3.select("#" + chart).append("svg")
                .style("margin-bottom", "10px")
                .attr("class", "case-svg")
                .attr("width", state_width + state_margin.left + state_margin.right)
                .attr("height", state_height + state_margin.top + state_margin.bottom)
                .append("g")
                .attr("transform", "translate(" + state_margin.left + "," + state_margin.top + ")");

            // add the Y gridlines
            svg4.append("g")
                .attr("class", "grid")
                .call(make_y_gridlines()
                    .tickSize(-state_width)
                    .tickFormat("")
                );

            /*
                   svg4.append("text")
                    .data([data])
                    .attr("x",function(d) {
                        return xState(parseDate("3/23/20"));
                    })
                    .attr("y", function(d) {
                        return yState(200);
                    })
                    .attr("class","order chartnote chartnote-sm")
                    .style("text-anchor", "middle")
                    .text("March 23");
                    
                   svg4.append("text")
                    .data([data])
                    .attr("x",function(d) {
                        return xState(parseDate("3/23/20"));
                    })
                    .attr("y", function(d) {
                        return yState(200);
                    })
                    .attr("dy",15)
                    .attr("class","order chartnote chartnote-sm lite")
                    .style("text-anchor", "middle")
                    .text("Stay-home order");
            
                  svg4.append("line")
                    .data([data])
                      .attr("class","order datenote pointer")
                      .attr("x1", function(d) {
                          return xState(parseDate("3/23/20"));
                      })
                      .attr("x2", function(d) {
                          return xState(parseDate("3/23/20"));
                      })
                      .attr("y1", function(d) {
                          return yState(200)+20;
                      })
                      .attr("y2", function(d) {
                          return yState(0);
                      });
            
                  svg4.append("text")
                    .data([data])
                    .attr("x",function(d) {
                        return xState(parseDate("5/15/20"));
                    })
                    .attr("y", function(d) {
                        return yState(200);
                    })
                    .attr("class","order datenote chartnote chartnote-sm")
                    .style("text-anchor", "middle")
                    .text("May 15");
                    
                   svg4.append("text")
                    .data([data])
                    .attr("x",function(d) {
                        return xState(parseDate("5/15/20"));
                    })
                    .attr("y", function(d) {
                        return yState(200);
                    })
                    .attr("dy",15)
                    .attr("class","order datenote chartnote chartnote-sm lite")
                    .style("text-anchor", "middle")
                    .text("Reopening begins");
            
                  svg4.append("line")
                    .data([data])
                      .attr("class","order datenote pointer")
                      .attr("x1", function(d) {
                          return xState(parseDate("5/15/20"));
                      })
                      .attr("x2", function(d) {
                          return xState(parseDate("5/15/20"));
                      })
                      .attr("y1", function(d) {
                          return yState(200)+20;
                      })
                      .attr("y2", function(d) {
                          return yState(0);
                      });
            */
            svg4.selectAll(".bar")
                .data(data)
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function (d) { return xState(d.date) - (rectwidth / 2); })
                .attr("height", function (d) {
                    return state_height - yState(d[chart]);
                })
                .attr("width", rectwidth)
                .attr("y", function (d) {
                    return yState(d[chart]);
                })
                .attr("fill", function (d, i) {
                    if (i == (data.length - 1)) {
                        return colorlist[chart].end;
                    } else {
                        return colorlist[chart].bar;
                    }
                })
                .on("mousemove", function (d) {
                    var datedisp = d.date;
                    var testnums = "";
                    if (chart == 'rates') {
                        var pos = +d.pos;
                        var neg = +d.neg;
                        var tot = pos + neg;
                        testnums = "<div>Tests: <strong>" + addCommas(tot) + "</strong></div>"
                            + "<div>Positives: <strong>" + addCommas(pos) + "</strong></div>";
                        var rate = (d[chart] * 100).toFixed(1) + "%";
                        var avg = (d.avg * 100).toFixed(1) + "%";
                    } else {
                        var rate = d[chart];
                        var avg = d.avg.toFixed(1);
                    }
                    if (!isNaN(d.avg)) {
                        var rate_avg = "Wk. avg: <strong>" + avg + "</strong>";
                        var height_adj = 60;
                    } else {
                        var rate_avg = "";
                        var height_adj = 50;
                    }
                    /*
                                  var xpos = xState(d.date)+state_margin.left-43;
                                  var ypos = yState(d[chart])-height_adj;
                                  if (xpos <= state_margin.left) {
                                      var xtool = state_margin.left;
                                  } else {
                                      xtool = xpos;
                                  }
                    */
                    var coords = d3.mouse(this);
                    var xpos = coords[0] + 43;
                    var ypos = coords[1];
                    var xtool = xpos;
                    if (xpos >= state_width + state_margin.right - 86) {
                        xtool = xpos - 116;
                    }


                    d3.select("#" + chart + " .datetip")
                        .classed("hidden", false)
                        .style("top", ypos + "px")
                        .style("left", xtool + "px");
                    d3.select("#" + chart + " .datetip .datedisp").text(formatDate(datedisp));
                    d3.select("#" + chart + " .datetip .ratedisp").html("Daily: <strong>" + addCommas(rate) + "</strong>");
                    d3.select("#" + chart + " .datetip .rateavg").html(rate_avg);
                    d3.select("#" + chart + " .datetip .testnums").html(testnums);
                    d3.select("#" + chart + " .data-circle.circle_" + formatClass(d.date))
                        .classed("hidden", false);

                })
                .on("mouseout", function (d) {
                    d3.selectAll("#" + chart + " .datetip,.data-circle")
                        .classed("hidden", true);
                });
/*
// This block does the 7-day average line and it's not working right yet.

            // Add the line path elements. 
            svg4.append("path")
                .data([data])
                .attr("class", "line")
                .style("stroke", "#fff")
                .style("stroke-width", 5)
                .attr("d", line);

            svg4.append("path")
                .data([data])
                .attr("class", "line")
                .style("stroke", colorlist[chart].line)
                .style("stroke-width", 3)
                .attr("d", line);



            svg4.append("text")
                .data([data])
                .attr("x", function (d) {
                    return xState(d[halfway].date);
                })
                .attr("y", function (d) {
                    return yState(d[halfway].avg) - 30;
                })
                .attr("dy", -3)
                .attr("class", "chartnote")
                .style("text-anchor", "left")
                .style("fill", colorlist[chart].line)
                .text('7-day average');

                svg4.append("line")
                .data([data])
                .attr("class", "pointer")
                .attr("x1", function (d) {
                    return xState(d[halfway].date) + 3;
                })
                .attr("x2", function (d) {
                    return xState(d[halfway].date) + 3;
                })
                .attr("y1", function (d) {
                    return yState(d[halfway].avg) - 30;
                })
                .attr("y2", function (d) {
                    return yState(d[halfway].avg);
                });

            var dots = svg4.append("g")
                .attr("class", "dots");


            dots.selectAll("dots")
                .data(data)
                .enter().append("circle")
                .attr("class", function (d) {
                    if (!isNaN(d.avg)) {
                        return "data-circle hidden circle_" + formatClass(d.date);
                    } else {
                        return "hidden";
                    }
                })
                .attr("r", 4)
                .style("fill", colorlist[chart].line)
                .style("stroke-width", "1px")
                .style("stroke", "#fff")
                .attr("cx", function (d) { return xState(d.date); })
                .attr("cy", function (d) { return yState(d.avg); });


            svg4.append("text")
                .data([data])
                .attr("x", function (d) {
                    return xState(d[data.length - 1].date);
                })
                .attr("y", function (d) {
                    return yState(d[data.length - 1][chart]) - 30;
                })
                .attr("class", "chartnote_" + chart + " chartnote chartnote-sm")
                .style("text-anchor", "middle")
                .text(function (d) {
                    return formatDate(d[data.length - 1].date);
                });
            svg4.append("text")
                .data([data])
                .attr("x", function (d) {
                    return xState(d[data.length - 1].date);
                })
                .attr("y", function (d) {
                    return yState(d[data.length - 1][chart]) - 30;
                })
                .attr("dy", 15)
                .attr("class", "chartnote_" + chart + " chartnote chartnote-sm lite")
                .style("text-anchor", "middle")
                .text(function (d) {
                    if (chart == 'rates') {
                        return ((d[data.length - 1][chart]) * 100).toFixed(1) + "%";
                    } else {
                        return addCommas(d[data.length - 1][chart]);
                    }
                });

            svg4.append("line")
                .data([data])
                .attr("class", "chartnote_" + chart + " pointer")
                .attr("x1", function (d) {
                    if (chart == 'rates') {
                        if (d[data.length - 1][chart] == 0) {
                            $(".chartnote_rates").css({ "display": "none" });
                        }
                    }
                    return xState(d[data.length - 1].date);
                })
                .attr("x2", function (d) {
                    return xState(d[data.length - 1].date);
                })
                .attr("y1", function (d) {
                    return yState(d[data.length - 1][chart]) - 12;
                })
                .attr("y2", function (d) {
                    return yState(d[data.length - 1][chart]);
                });





*/





            // attempt to add axes
            svg4.append("g")
                .attr("id", "yAxisG")
                .attr("class", "axis")
                .call(d3.axisLeft(yState).ticks(5).tickFormat(d3.format(ticker[chart])));

            svg4.append("g")
                .attr("id", "xAxisG")
                .attr("class", "axis")
                .attr("transform", "translate(0," + state_height + ")")
                .call(d3.axisBottom(xState).ticks(5).tickSizeOuter(0));


            d3.selectAll("path.domain").remove();
            d3.selectAll(".axis line").remove();

        });



}
