odoo.define('survey_score_template.pages', function (require) { 'use strict';

  require('web.dom_ready');
  var core = require('web.core');
  var _t = core._t;

  $(".breadcrumb").hide();

  $('form').on('submit', function(e) {
      // div to error
      var error = '<div class="js_errzone alert alert-danger" style="" role="alert"><p>Esta pregunta requiere una respuesta.</p></div>'
      var stop = 0;
      $(".optional").each(function() {
          // the actual div closest "js_question" and find the prev 
          var actual_section = $(this).closest(".js_question-wrapper");
          var prev_section = $(actual_section).prev(".js_question-wrapper");
          var radio = $(actual_section).find("input[type='radio']:checked").length;
          var total = $(actual_section).find("tbody tr").length;
          // buttons inside section
          var buttons = $(prev_section).find("input[type='radio']")
          $(buttons).each(function() {
              // if the button is checked and value is "yes"
              var checked = $(this).is(":checked");
               console.log(checked)
              if (checked == true) {
                  // value to input
                  var res = $(this).attr("colval").toLowerCase();
                  console.log(res);
                  if (res == "si") {
                      // remove error
                      $(actual_section).find('.js_errzone').remove();
                      // add error
                      $(actual_section).append(error);
                      // to stop the submit
                      if (radio != total) {
                          stop = 1;
                      }
                      // delete the msj
                      else{
                          $(actual_section).find('.js_errzone').remove();
                      }
                  }
                  else{
                      // clean section if the input is "not"
                      clean(actual_section)
                      // remove error
                      $(actual_section).find('.js_errzone').remove();
                  }
              }
          });
      });
      // stop the original submit
      if (stop == 1) {
          e.preventDefault();
          return false;
      }
  });

  // clean section
  function clean(section){
      $(section).each(function(i) {
          $(this).find("input[type='radio']").prop("checked",false);
      });
   }

  // hidde title "{{hidden}}"
  $(".js_question-wrapper span").each(function() {
    var question = $(this).text();
    if (question == "{{hidden}}") {
      $(this).closest("h2").hide();
          var actual = $(this).closest(".js_question-wrapper");
          var tbody = $(actual).find("table tbody").html();
          var prev = $(this).closest(".js_question-wrapper").prev(".js_question-wrapper");
          $(prev).find("tbody").append(tbody)
          $(actual).remove();
    }
  });

});