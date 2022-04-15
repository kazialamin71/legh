(function ($) {
  'use strict';
  $(function () {
    var test;


    var lineStatsOptions = {
      scales: {
        yAxes: [{
          display: false
        }],
        xAxes: [{
          display: false
        }]
      },
      legend: {
        display: false
      },
      elements: {
        point: {
          radius: 0
        },
        line: {
          tension: 0
        }
      },
      stepsize: 100
    }

    if ($('#stats-line-graph-1').length) {

      var lineChartCanvas = $("#stats-line-graph-1").get(0).getContext("2d");
      var gradientStrokeFill_1 = lineChartCanvas.createLinearGradient(0, 0, 0, 50);
      gradientStrokeFill_1.addColorStop(0, 'rgba(131, 144, 255, 0.5)');
      gradientStrokeFill_1.addColorStop(1, '#fff');
      var lineChart = new Chart(lineChartCanvas, {
        type: 'line',
        data: {
          labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", "Day 11", "Day 12", "Day 13"],
          datasets: [{
            label: 'Profit',
            data: [7, 6, 9, 7, 8, 6, 8, 5, 7, 8, 6, 7, 7],
            borderColor: '#6d7cfc',
            backgroundColor: gradientStrokeFill_1,
            borderWidth: 3,
            fill: true
          }]
        },
        options: lineStatsOptions
      });
    }
    if ($('#stats-line-graph-2').length) {
      var lineChartCanvas = $("#stats-line-graph-2").get(0).getContext("2d");
      var gradientStrokeFill_1 = lineChartCanvas.createLinearGradient(0, 0, 0, 50);
      gradientStrokeFill_1.addColorStop(0, 'rgba(131, 144, 255, 0.5)');
      gradientStrokeFill_1.addColorStop(1, '#fff');
      var lineChart = new Chart(lineChartCanvas, {
        type: 'line',
        data: {
          labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", "Day 11", "Day 12", "Day 13"],
          datasets: [{
            label: 'Profit',
            data: [7, 6, 8, 5, 7, 8, 6, 7, 7, 6, 9, 7, 8],
            borderColor: '#6d7cfc',
            backgroundColor: gradientStrokeFill_1,
            borderWidth: 3,
            fill: true
          }]
        },
        options: lineStatsOptions
      });
    }
    if ($('#stats-line-graph-3').length) {
      var lineChartCanvas = $("#stats-line-graph-3").get(0).getContext("2d");
      var gradientStrokeFill_1 = lineChartCanvas.createLinearGradient(0, 0, 0, 50);
      gradientStrokeFill_1.addColorStop(0, 'rgba(131, 144, 255, 0.5)');
      gradientStrokeFill_1.addColorStop(1, '#fff');
      var lineChart = new Chart(lineChartCanvas, {
        type: 'line',
        data: {
          labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", "Day 11", "Day 12", "Day 13"],
          datasets: [{
            label: 'Profit',
            data: [8, 6, 7, 8, 5, 7, 9, 7, 8, 7, 6, 7, 6],
            borderColor: '#6d7cfc',
            backgroundColor: gradientStrokeFill_1,
            borderWidth: 3,
            fill: true
          }]
        },
        options: lineStatsOptions
      });
    }
    if ($('#stats-line-graph-4').length) {
      var lineChartCanvas = $("#stats-line-graph-4").get(0).getContext("2d");
      var gradientStrokeFill_1 = lineChartCanvas.createLinearGradient(0, 0, 0, 50);
      gradientStrokeFill_1.addColorStop(0, 'rgba(131, 144, 255, 0.5)');
      gradientStrokeFill_1.addColorStop(1, '#fff');
      var lineChart = new Chart(lineChartCanvas, {
        type: 'line',
        data: {
          labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7", "Day 8", "Day 9", "Day 10", "Day 11", "Day 12", "Day 13"],
          datasets: [{
            label: 'Profit',
            data: [7, 6, 8, 5, 8, 6, 8, 7, 8, 6, 9, 7, 7],
            borderColor: '#6d7cfc',
            backgroundColor: gradientStrokeFill_1,
            borderWidth: 3,
            fill: true
          }]
        },
        options: lineStatsOptions
      });
    }

  });
})(jQuery);