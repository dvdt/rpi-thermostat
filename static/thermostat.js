var Root = React.createClass({
  getInitialState: function() {
    var setpoints = {"0": 75, "3": 75, "6": 75, "9": 75, "12": 75, "15": 75, "18": 75, "21": 75};
    return {"setpoints": setpoints};
  },
  handleSetpointChange: function(hour, newSetpoint) {
    console.log(hour + ": " + newSetpoint);
    this.state.setpoints[hour] = newSetpoint;
    this.setState(this.state);
  },
  render: function() {
    return (
    <div className="row">
      <div className="col-md-2"></div>
      <div className="col-md-4">
        <div className="row">
          <div className="col-md-12" style={{padding: "10px"}}>
            <SubmitSetpoints />
          </div>
        </div>
        <div className="row">
          <div className="col-md-12">
            <div className="center-block">
              <SetpointClockGraphic height="300" width="300" setpoints={this.state.setpoints} />
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-4">
        <TempSetpoints setpoints={this.state.setpoints} handleSetpointChange={this.handleSetpointChange} />
      </div>
      <div className="col-md-2"></div>
    </div>
    );
  }
});

var SubmitSetpoints = React.createClass({
  render: function() {
    return (
    <button className="btn center-block">
      Set thermostat
    </button>
    );
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
        console.log(hr + " -> " + setpoints[hr]);
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
    var rAxis = d3.svg.axis().scale(axisScale)
      .tickValues([60, 80, 100])
      .orient('bottom');

    var rMinorAxis =d3.svg.axis().scale(axisScale)
      .tickSize(4)
      .tickValues([50,55,65,70,75,85,90,95])
      .orient('bottom').tickFormat("");

    var color = d3.scale.quantile()
      .domain([32,50,60,65,70,75,80,90,100])
      .range(["rgb(69,117,180)", "rgb(116,173,209)", "rgb(171,217,233)",
              "rgb(224,243,248)", "rgb(254,224,144)", "rgb(253,174,97)", "rgb(244,109,67)",
              "rgb(215,48,39)"]);

    var arc = d3.svg.arc()
      .outerRadius(function(d) {return rScale(d.temp);})
      .innerRadius(rScale(50))
      .startAngle(function (d) {return arcScale(d.hr);})
      .endAngle(function (d) {return arcScale(d.hr+3);});

    var svg = d3.select(svgEl).select("g");
    var g = svg.selectAll(".arc")
      .data(data)
    .enter().append("g")
      .attr("class", "arc");

    g.append("path")
        .attr("d", arc)
        .style("fill", function(d) { return color(+d.temp); });

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

  componentWillUnmount: function() {
    var el = React.findDOMNode(this);

  },

  render: function() {
    return (
      <svg key={JSON.stringify(this.props.setpoints)} id="setpoints-clock" className="center-block">
      </svg>
      );
  }});

React.render(<Root />, document.getElementById('root'));