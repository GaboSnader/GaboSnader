odoo.define('survey.survey.photo', function (require) {
'use strict';

  require('web.dom_ready');
  var core = require('web.core');
  var _t = core._t;

  $( document ).ready(function() {
      var camera = "#my_camera"
      if($(camera).length != 0) {
        Webcam.attach(camera);
        Webcam.set({
          width: 500,
          height: 376,
          dest_width: 500,
          dest_height: 376,
          image_format: 'jpeg',
          jpeg_quality: 90,
          force_flash: false,
          fps: 45,
          swfURL: '/survey_take_photo/static/src/js/webcam.swf',
        });
      }
  });

  $("#take").click(function() {
      Webcam.freeze();
      $("#take").hide();
      $("#take_new").show();
      $("#accept").show();
  });

  $("#take_new").click(function() {
      Webcam.unfreeze();
      $("#picture").val("")
      $("#take_new").hide();
      $("#take").show();
      $("#accept").hide();
  });

  $("#accept").click(function() {
      $("#take").hide();
      $("#take_new").hide();
      $("#accept").hide();
      $("#continue").show();
  });

  $("#continue").click(function() {
      Webcam.snap(function(image) {
        $("#picture").val(image)
      });
  });

});