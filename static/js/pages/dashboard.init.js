!function ( e ) { "use strict"; var a = function () { this.$realData = [] }; a.prototype.createDonutChart = function ( e, a, r ) { Morris.Donut( { element: e, data: a, resize: !0, colors: r, backgroundColor: "transparent" } ) }, a.prototype.init = function () { this.createDonutChart( "morris-donut-example", [ { label: "Accuracy", value: 90 }, { label: "Accuracy", value: 89.64 }, { label: "Accuracy", value: 88 } ], [ "#ff8acc", "#5b69bc", "#35b8e0" ] ) }, e.Dashboard1 = new a, e.Dashboard1.Constructor = a }( window.jQuery ), function ( e ) { "use strict"; window.jQuery.Dashboard1.init() }();