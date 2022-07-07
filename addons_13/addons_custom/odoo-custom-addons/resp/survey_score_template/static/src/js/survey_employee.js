odoo.define('survey_score_template.employee', function (require) {
'use strict';

  require('web.dom_ready');
  var core = require('web.core');
  var _t = core._t;

  var level_sf = $("input[name='level-sf']");
  var level_primary = $("input[name='level-primary']");
  var level_secondary = $("input[name='level-secondary']");
  var level_preparatory = $("input[name='level-preparatory']");
  var level_technical = $("input[name='level-technical']");
  var level_degree = $("input[name='level-degree']");
  var level_mastery = $("input[name='level-mastery']");
  var level_doctorate = $("input[name='level-doctorate']");

  $('#form_employee').on('submit', function(e) {
    var input = $("input[type=hidden]");
    var sex = $("input[name='sex']:checked").length;
    var year = $("input[name='year']:checked").length;
    var job_type = $("input[name='job_type']:checked").length;
    var contract_type = $("input[name='contract_type']:checked").length;
    var personal_type = $("input[name='personal_type']:checked").length;
    var jornal_type = $("input[name='jornal_type']:checked").length;
    var turn = $("input[name='turn']:checked").length;
    var experience_job = $("input[name='experience_job']:checked").length;
    var experience_work = $("input[name='experience_work']:checked").length;
    var nulls = 0;

    if (sex == 0) {
      $(".sex").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".sex").css({'background-color':'#ffffff'});
    }

    if (year == 0) {
      $(".year").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".year").css({'background-color':'#ffffff'});
    }

    if (job_type == 0) {
      $(".job_type").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".job_type").css({'background-color':'#ffffff'});
    }

    if (contract_type == 0) {
      $(".contract_type").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".contract_type").css({'background-color':'#ffffff'});
    }

    if (personal_type == 0) {
      $(".personal_type").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".personal_type").css({'background-color':'#ffffff'});
    }

    if (jornal_type == 0) {
      $(".jornal_type").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".jornal_type").css({'background-color':'#ffffff'});
    }

    if (turn == 0) {
      $(".turn").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".turn").css({'background-color':'#ffffff'});
    }

    if (experience_job == 0) {
      $(".experience_job").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".experience_job").css({'background-color':'#ffffff'});
    }

    if (experience_work == 0) {
      $(".experience_work").css({'background-color':'#ffd4d8'});
      nulls = 1;
    }
    else{
      $(".experience_work").css({'background-color':'#ffffff'});
    }

    if (nulls == 1) {
      e.preventDefault();
    }

  });
  $(level_sf).change(function() {
    if (this.checked) {
      $(level_primary).prop("disabled",true).prop('checked',false);
      $(level_secondary).prop("disabled",true).prop('checked',false);
      $(level_preparatory).prop("disabled",true).prop('checked',false);
      $(level_degree).prop("disabled",true).prop('checked',false);
      $(level_mastery).prop("disabled",true).prop('checked',false);
      $(level_doctorate).prop("disabled",true).prop('checked',false);
      $(level_technical).prop("disabled",true).prop('checked',false);
    }
    else{
      $(level_primary).prop("disabled",false);
      $(level_secondary).prop("disabled",false);
      $(level_preparatory).prop("disabled",false);
      $(level_degree).prop("disabled",false);
      $(level_mastery).prop("disabled",false);
      $(level_doctorate).prop("disabled",false);
      $(level_technical).prop("disabled",false);
    }
  });

});