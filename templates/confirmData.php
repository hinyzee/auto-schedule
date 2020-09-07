<html>

  <head>
    <link rel="stylesheet" type="text/css" media="all" href="static/hi.css"/>
  </head>

  <body>
    <h1>ADD THESE EVENTS TO YOUR CALENDAR?</h1>


    <form action="sendData" method="post">
      Adding events from: <input type="date" name="startDate" value={{data["startDate"]}}>
      to: <input type="date" name="endDate" value={{data["endDate"]}}> <br>
       <br> <br>

      <button type="button" onclick="createRow()">New Event</button> <br>

      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>(Weekly) Date(s)</th>
            <th>Location</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Description</th>
            <th>delete</th>
          </tr>
        </thead>
        <tbody id="tableBody">
        </tbody>
      </table>
      <input type="submit" name="submit" value="Add These Events">
      <input id="hiddenInput" type="hidden" name="numRows" value="0">

      <br>Calendar Name: <input type="text" name="name" id="cal_name">

    </form>



  </body>

</html>

<script type="text/javascript">
  var numRows = 0;

  function createInput(attr){
    var res = document.createElement("input");
    for (var key in attr){
      res.setAttribute(key, attr[key]);
    }
    return res;
  }

  function get_key(obj, key, def){
    var res = obj[key];
    return (typeof res === 'undefined') ? def : res;
  }

  function deleteRow(ele){
    numRows -= 1;
    document.getElementById("hiddenInput").setAttribute("value", numRows.toString());

    ele.parentElement.remove();
    var tab = document.getElementById("tableBody");
    for (var i=0; i<tab.rows.length; i++){
      var row = tab.rows[i];
      for (var j=0; j<row.cells.length; j++){
        var col = row.cells[j];
        for (var k=0; k<col.children.length; k++){
          var inn = col.children[k];
          var x = inn.getAttribute("name");
          x = x.replace(/0|1|2|3|4|5|6|7|8|9/g, "");
          x = x[0] + String(i+1) + x.substring(1);
          inn.setAttribute("name", x);
        }
      }
    }
  }

  function createRow(val={}){
    numRows += 1;
    document.getElementById("hiddenInput").setAttribute("value", numRows.toString());

    var types = ["text","text", "text",   "time", "time","text"];
    var names = ["title","date","location","start", "end",  "description"];

    var n = types.length;
    var row = document.createElement("tr");
    for (var i=0; i<n; i++){
      var td = document.createElement("td");
      var myName = "R"+numRows+names[i]
      if (types[i] == "time"){
        td.appendChild(createInput({type: "number",
          name: myName+"H", min: "0", max: "23", step:"1",
          value: get_key(val, names[i]+"H", ""), required:"",
        }));
        td.innerHTML += ":";
        td.appendChild(createInput({type: "number",
          name: myName+"M", min: "0", max: "59", step:"1",
          value: get_key(val, names[i]+"M", ""), required:"",
        }));
      } else {
        var obj = {type: types[i], name: myName, value: get_key(val, names[i], "")}
        if (names[i] == "date"){obj["required"]="";}
        td.appendChild(createInput(obj));
      }
      row.appendChild(td);
    }

    var bb = document.createElement("button");
    bb.setAttribute("type", "button");
    bb.setAttribute("onclick", "deleteRow(this)");
    row.appendChild(bb);

    document.getElementById("tableBody").appendChild(row);
  }

  window.onload = function(){
    var vvv = {{data["values"]}};
    for (var i=0; i<{{data["numRows"]}}; i++){
      createRow(get_key(vvv, i, {}));
    }
    if ({{data["alert"]}}){
      alert("Are you sure the input is from WebReg?");
    }

    document.getElementById("cal_name").setAttribute("value", "webregCourses");
  };
</script>
