odoo.define('survey_score_template.terms', function (require) {
'use strict';

  require('web.dom_ready');
  var core = require('web.core');
  var _t = core._t;

  $("#terms").click(function() {
    $(".politic").hide()
    $(".terms").fadeIn("slow")
  });

  $("#politic").click(function() {
    $(".terms").hide()
    $(".politic").fadeIn("slow")
  });

  $('.check').change(function() {
    var terms = $("#check1").is(':checked');
    var politic = $("#check2").is(':checked');
    if (terms == true && politic == true) {
      $(".continue").fadeIn("slow");
    }
    else{
      $(".continue").hide();
    }
  });

});