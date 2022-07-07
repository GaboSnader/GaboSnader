odoo.define('survey_score_template.traumatic', function (require) {
'use strict';

  require('web.dom_ready');
  var core = require('web.core');
  var _t = core._t;

  function hideSections() {
    console.log('Ejecutando hideSection');
    $(".section-two").closest("tr").hide();
    $(".section-tree").closest("tr").hide();
    $(".section-four").closest("tr").hide();
}
document.onload = hideSections();
window.onload = hideSections(); 


  $('#form_traumatic').on('submit', function(e) {
    // var url_traumatic = $("#url_traumatic").val();
    var url_not_traumatic = $("#url_not_traumatic").val();
    var required = false;
    var first_no = 0;
    var first_yes = 0;
    var apply = 0;
    
    if ($(".first:checked").length == 0) {
        $(".first").closest("tr").css({'background-color':'#ffd4d8'});
        return false
    }
    else if ($(".first:checked").length == 6){
        $(".first").closest("tr").css({'background-color':'#ffffff'});
    }
    else{
        return false
    }
    $.each($(".first:checked"), function(key,value){
        var first = $(value).val();
        if (first == "No") {
            first_no += 1;
        }
        else if (first == "Si"){
            first_yes += 1;
        }
    });

    if (first_no == 6) {
        e.preventDefault()
        window.location.href = url_not_traumatic;
    }
    if (first_yes > 0){
        required = true;
    }
    else{
        required = false;
    }

    var second_yes = 0;
    $.each($(".second:checked"), function(key,value){
        var second = $(value).val()
        if (second == "Si") {
            second_yes += 1;
        }
    });

    if (second_yes >= 1) { 
        apply += 1}
    var tree_yes = 0;
    $.each($(".tree:checked"), function(key,value){
        var tree = $(value).val()
        if (tree == "Si") {
            tree_yes += 1;
        }
    });

    if (tree_yes >= 3) { 
        apply += 1}
    var four_yes = 0;
    $.each($(".four:checked"), function(key,value){
        var four = $(value).val()
        if (four == "Si") {
            four_yes += 1;
        }
    });

    if (four_yes >= 2) { 
        apply += 1}
    if (required != true) {
        $(".second").closest("tr").css({'background-color':'#ffffff'});
        $(".tree").closest("tr").css({'background-color':'#ffffff'});
        $(".four").closest("tr").css({'background-color':'#ffffff'});
    }
    else{
        $(".section-two").closest("tr").show();
        $(".section-tree").closest("tr").show();
        $(".section-four").closest("tr").show();
        $(".second").closest("tr").css({'background-color':'#ffd4d8'});
        $(".tree").closest("tr").css({'background-color':'#ffd4d8'});
        $(".four").closest("tr").css({'background-color':'#ffd4d8'});
        var answer = answered();
        if (answer != true) {
            return false
        }
        if (apply != 3){
            e.preventDefault()
            window.location.href = url_not_traumatic;
        }
    }
  });
  function answered(){
      var res = false;
      var section = 0;
      if ($(".first:checked").length == 6){
          section += 1;
      }
      if ($(".second:checked").length == 2){
          section += 1;
      }
      if ($(".tree:checked").length == 7){
          section += 1;
      }
      if ($(".four:checked").length == 5){
          section += 1;
      }
      if (section == 4) {
          res = true;
      }
      
      return res
  }

});