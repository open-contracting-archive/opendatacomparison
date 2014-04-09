var cellSize = 20,
    itemsPerColumn = 5,
    blockheight = cellSize * itemsPerColumn,
    width = 1200,
    height = 70 + blockheight,
    //initializes blockx & blockwidth which is used in loops to store prev
    blockx = 0,
    blockwidth = 0,
    requiredblocks = ['UK Bids', 'UK Awards'];

function getRow(id) {
    row = id % itemsPerColumn;
    return row;
}

function getColumn(id) {
    return Math.floor(id / itemsPerColumn);
}

function getBlockWidth(elements) {
    elementcount = elements.length;
    numberofcolumns = Math.ceil(elementcount/itemsPerColumn);
    blockwidth = numberofcolumns * cellSize;
    return blockwidth
}

function getQuestionColor(question) {
    questioncolor = "#CCC"
    if (question['hasmap'] === "True") {
        questioncolor = "#6FA2FF";
    }
    if (!question.hasOwnProperty('hasmap')) {
        questioncolor = "#FFD48E";
    }
    return questioncolor
}

d3.json("data.json", function(error, json){

    // Add an svg to the visualizatoin div
    var svg = d3.select(".visualization")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

    // Add g groups for each parent concepts
    var parentconcept = svg.selectAll(".parentconcept")
                           .data(json)
                           .enter().append("g")
                           .attr({
                               "class": (function(d) { return "parentconcept" + " " + d.conceptname }),
                               "transform": (function(d, i) { amount = 10 + i*100; return "translate(" + amount +", 0)" })
                           })

    var childconcept = parentconcept.selectAll('.childconcept')
                                    .data(function(d) { return d.children })
                                    .enter().append("g")
                                    .attr({
                                        "class": (function(d) { return "childconcept" + " " + d.conceptname }),
                                        "transform": (function(d, i) { amount = 10 + i*65; return "translate(0, " + amount +")" })
                                    })

    childconcept.selectAll(".question")
                 .data(function(d) { return d.items })
                 .enter().append("rect")
                 .attr({
                     "class": "question",
                     "x": (function(d, i) { return cellSize*getColumn(i) }),
                     "y": (function(d, i) { return blockheight - cellSize*(getRow(i)+1) }),
                     "width": cellSize,
                     "height": cellSize,
                     "fill": getQuestionColor,
                     "stroke": "#fff",
                     "stroke-weight": "1px"
                 });

});
