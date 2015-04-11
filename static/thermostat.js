var Root = React.createClass({
  getInitialState: function() {
    var setpoints = {"0": 75, "3": 75, "6": 75, "9": 75, "12": 75, "15": 75, "18": 75, "21": 75};
    return {"setpoints": setpoints,
            "altered": false};
  },

  componentDidMount: function() {
    $.ajax("/api/v1/timer/", {
      type: "GET",
      success: function(data, status, req) {
        console.log(data);
//        this.state.altered = false
//        this.state.setpoints = data;

        this.setState(data);
      }.bind(this),
      error: function(xhr, status, err) {console.error("setpoint post error", status, err.toString());}
    });
  },
  handleSetpointChange: function(hour, newSetpoint) {
    this.state.setpoints[hour] = newSetpoint;
    this.state.altered = true;
    this.setState(this.state);
  },
  /**
  * Sends ajax request to server to change temp setpoints
  */
  setSetpoints: function() {
    $.ajax("/api/v1/setpoints/", {
      type: "POST",
      data: {"setpoints": JSON.stringify(this.state.setpoints)},
      success: function(data, status, req) {
        this.state.altered = false;
        this.setState(this.state);
      }.bind(this),
      error: function(xhr, status, err) {console.error("setpoint post error", status, err.toString());}
    });
  },

  setManualState: function(data) {
    if (data.future_sec) {
      this.setState(data);
    }
  },
  setManual: function(on_time) {
    $.ajax("/api/v1/timer/", {
      type: "POST",
      data: {"on_time": on_time},
      success: function(data, status, req) {
        this.setManualState(data);
      }.bind(this),
      error: function(xhr, status, err) {console.error("setpoint post error", status, err.toString());}
    });
  },

  render: function() {
    return (
    <div>
    <div className="row">
      <div className="col-md-offset-2 col-md-10">
        <div className="center-block"><h3>Turn AC on for:</h3></div>
      </div>
    </div>
    <div className="row">

      <div className="col-md-offset-2 col-md-10">
        <ManualTimer handleManual={this.setManual} />
      </div>

      <div className="col-md-2"></div>

      <div className="row">
        <div className="col-md-6 center-block">
          <p>{this.state.future_sec ? (this.state.future_status ? "turning on in " : "turning off in ") + parseInt(this.state.future_sec / 60) + " minutes" : null}</p>
        </div>
      </div>
    </div>
    </div>
    );
  }
});

var ManualTimer = React.createClass({
  handleClick: function(e) {
    console.log(e);
    var val = e.target.value;
    this.props.handleManual(val);
  },
  render: function() {
    return (
    <div className="row">
      <div className="col-md-3 manual-override">
        <button className="btn btn-primary" value={30*60} onClick={this.handleClick}>30 min ($0.10)</button>
      </div>
      <div className="col-md-offset-1 col-md-3 manual-override">
        <button className="btn btn-success" value={60*60} onClick={this.handleClick}>1 hr ($0.20)</button>
      </div>
      <div className="col-md-offset-1 col-md-3 manual-override">
        <button className="btn btn-warning" value={120*60} onClick={this.handleClick}>2 hr ($0.40)</button>
      </div>
    </div>
    );
  }
});
var SubmitSetpoints = React.createClass({
  render: function() {
    if (this.props.altered) {
    return (
    <button id="submit-temps" className="btn btn-warning center-block" onClick={this.props.handleClick}>
      Set thermostat
    </button>
    );
    } else {
    return (
      <button id="submit-temps" className="btn btn-info center-block" disabled="disabled">
      Set thermostat
    </button>
    );
    }

  }
});

var TempSetpoints = React.createClass({
  getLabelledSlider: function(hour, label) {
    var elemId = "temp-setpoint-" + hour;
    return (
      <div className="form-group">
        <label className="col-md-4 control-label" htmlFor={elemId}><p className="text">{label}</p></label>
        <div className="col-md-8" >
          <TempSetpointSlider id={elemId} className="form-control" hour={hour} min="65" max="85" value={this.props.setpoints[hour]} handleSetpointChange={this.props.handleSetpointChange} />
        </div>
      </div>
    );
  },
  render: function() {
    return (
      <div className="form-horizontal">
        <div className="form-group">
          <div className="col-md-offset-4 col-md-1">65F</div>
          <div className="col-md-7 text-right">85F</div>
        </div>
        {this.getLabelledSlider("0", "midnight - 3am")}
        {this.getLabelledSlider("3", "3am - 6am")}
        {this.getLabelledSlider("6", "6am - 9am")}
        {this.getLabelledSlider("9", "9am - noon")}
        {this.getLabelledSlider("12", "noon - 3pm")}
        {this.getLabelledSlider("15", "3pm - 6pm")}
        {this.getLabelledSlider("18", "6pm - 9pm")}
        {this.getLabelledSlider("21", "9pm - midnight")}
      </div>
    );
  }
});

var TempSetpointSlider = React.createClass({
  handleSetpoint: function(setpointEvent) {
    this.props.handleSetpointChange(this.props.hour, setpointEvent.target.value);
  },
  render: function() {
    return (
    <input id={this.props.id} type="range" min={this.props.min} className="form-control"
                    max={this.props.max}  value={this.props.value} onChange={this.handleSetpoint}/>
    )
  }});

var SetpointClockGraphic = React.createClass({
  toArcData: function(setpoints) {
    var data = [];
    for (var hr in setpoints) {
      if (setpoints.hasOwnProperty(hr)) {
        data.push({"hr": +hr, "temp": setpoints[hr]});
      }
    }
    return data;
},

  createClock: function(svgEl) {
    var width = this.props.width;
    var height = this.props.height;
    var svg = d3.select(svgEl)
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
  },

  updateClock: function(svgEl, data) {
    var width = this.props.width - 50;
    var height = this.props.height - 50;
    var radius = Math.min(width, height) / 2;
    var arcScale = d3.scale.linear().domain([0,24]).range([Math.PI, 3*Math.PI]);
    var rScale = d3.scale.linear().domain([32, 100]).range([0, radius]);
    var axisScale = d3.scale.linear().domain([50, 100]).range([rScale(50), rScale(100)]);
    var color = d3.scale.quantile()
      .domain([32,50,60,65,70,75,80,90,100])
      .range(["rgb(69,117,180)", "rgb(116,173,209)", "rgb(171,217,233)",
              "rgb(224,243,248)", "rgb(254,224,144)", "rgb(253,174,97)", "rgb(244,109,67)",
              "rgb(215,48,39)"]);

    var rAxis = d3.svg.axis().scale(axisScale)
      .tickValues([60, 80, 100])
      .orient('bottom');

    var rMinorAxis =d3.svg.axis().scale(axisScale)
      .tickSize(4)
      .tickValues([50,55,65,70,75,85,90,95])
      .orient('bottom').tickFormat("");

    var tempArc = d3.svg.arc()
      .outerRadius(function(d) {return rScale(d.temp);})
      .innerRadius(rScale(50))
      .startAngle(function (d) {return arcScale(d.hr);})
      .endAngle(function (d) {return arcScale(d.hr+3);});

    var hrArc = d3.svg.arc()
                .outerRadius(radius+15)
                .innerRadius(radius+15)
                .startAngle(function (d) {return arcScale(d.hr);})
                .endAngle(function (d) {return arcScale(d.hr);});

    var svg = d3.select(svgEl).select("g");
    var g = svg.selectAll(".arc")
      .data(data)
    .enter().append("g")
      .attr("class", "arc");

    g.append("path")
        .attr("d", tempArc)
        .style("fill", function(d) { return color(+d.temp); });
    g.append("text")
        .attr("transform", function(d) {return "translate("+tempArc.centroid(d)+")"})
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(function(d) {
          return d.temp + 'F';
        });
    g.append("text")
          .attr("transform", function(d) {return "translate("+hrArc.centroid(d)+")";})
          .attr("dy", ".35em")
          .style("text-anchor", "middle")
          .text(function(d) {
            if (d.hr===12)
              return '12 - noon'
            if (d.hr===0)
              return '0 - midnight';
            return d.hr;});

    // Add the r-axis.
    svg.append("g")
        .attr("class", "x axis")
        .call(rAxis.orient("bottom"));
    svg.append("g")
        .attr("class", "x axis")
        .call(rMinorAxis.orient("bottom"));

    // Add the negative r-axis.
    svg.append("g")
        .attr("class", "x axis")
        .call(rAxis.orient("bottom").scale(axisScale.copy().range([-rScale(50), -rScale(100)])));
    svg.append("g")
        .attr("class", "x axis")
        .call(rMinorAxis.orient("bottom").scale(axisScale.copy().range([-rScale(50), -rScale(100)])));
  },

  componentDidMount: function() {
    var el = React.findDOMNode(this);
    this.createClock(el);
    this.updateClock(el, this.toArcData(this.props.setpoints));
  },

  componentDidUpdate: function() {
    var el = React.findDOMNode(this);
    this.createClock(el);
    this.updateClock(el, this.toArcData(this.props.setpoints));
  },

  render: function() {
    return (
      <svg key={JSON.stringify(this.props.setpoints)} id="setpoints-clock" className="center-block">
      </svg>
      );
  }});

React.render(<Root />, document.getElementById('root'));