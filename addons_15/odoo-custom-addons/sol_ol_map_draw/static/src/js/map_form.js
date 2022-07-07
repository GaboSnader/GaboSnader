odoo.define('solver_map_form.widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');

var solmap_common = require('sol_ol_map_draw.solmap_common');

var MapFormWidget = AbstractField.extend(solmap_common.SolMapMixin,{
    className: "o_map_form",
    template: 'SolMapFormField',
    events: {
        'click #solMapFormEditProp': '_saveEditPropFeature',
        'click #solMapFormCloseProp': '_closeEditPropFeature',
        'click #solMapFormCloseDraw': '_closeDrawFeature',
    },

    init: function(parent, data, options, recordOptions){
        var sup =this._super.apply(this, arguments);
        this.url = {
                    nominatim : 'https://nominatim.openstreetmap.org/',
                    google:'https://maps.googleapis.com/maps/api/geocode/json',
                    };
        this.format ={
                     nominatim_format:'geocodejson',
                     };
        this.service = {
                        nominatim_reverse:'reverse',
                        nominatim_search:'search',
                        };
        this.data = this.recordData;
        this.placemark = {};
        this.isDrawingStart = false;
        this.isRemoveStart = false;
        this.isEditStart = false;
        this._SelectedFeature={};
        // // reverse : latlng=40.714224,-73.961452 and search : address=
        //this.key['google'] ='AIzaSyBKm7hchNf6N6GVZhTyeQ5zK2PDj_4S_5s';
        return sup;
    },

    start: function() {
        if (!this.value){
            this.value ='Empty';
        }
        var self = this;
        var olmapdiv= this.$(".olmapform");
        var map = this._renderMap();
        map.setTarget(olmapdiv.get(0));
        this._renderDraggableMarker();
        self.$(".o_geocoding_solform").hide();
        var $_geCodeButton  = self.$("#sol-geocode");

        this._initInteraction();
        if (self.mode==='edit' && !this.get('effective_readonly')){
            self._createDrawingControl();
            self._createRemoveControl();
            self._createEditFeaturesControl();
            self.$(".startDraw").click(self._OnStartDraw.bind(self));
            $_geCodeButton.click(self._on_geCodeButtonClick.bind(self));

            if (this.nodeOptions.geocode_btn){
                if(parseInt(this.nodeOptions.geocode_btn) ===0){
                    console.log("disabled",this.nodeOptions.geocode_btn);
                    $_geCodeButton.attr("disabled","disabled");
                    $_geCodeButton.hide();
                }
            }
        }else{
            $_geCodeButton.attr("disabled","disabled");
            $_geCodeButton.hide();
        }
        return this._super.apply(this, arguments);
    },

    _initInteraction : function(){
        // layer declaration for interaction
        if (!this.vectorSource ){
            this.vectorSource = new ol.source.Vector();
        }
        if(this.value && this.value != 'Empty'){
            this.vectorSource.addFeatures(new ol.format.GeoJSON().readFeatures(this.value));
            self =this;
            _.each(this.vectorSource.getFeatures(), function(feature){
                var props = {
                    fill_color: (feature.get('fill_color') ? feature.get('fill_color'): 'rgba(255, 255, 255, 0.5)'),
                    stroke_color: (feature.get('stroke_color') ? feature.get('stroke_color'): '#ffcc33'),
                    stroke_width: (feature.get('stroke_width') ? feature.get('stroke_width'): 2),
                    image_radius: (feature.get('image_radius') ? feature.get('image_radius'): 7),
                    image_fill_color: (feature.get('image_fill_color') ? feature.get('image_fill_color'): '#ffcc33'),
                };
                feature.setStyle(self._getStyle(props));
            });
        }
        if (!this.vectorLayer ){
            this.vectorLayer = new ol.layer.Vector({
              source: this.vectorSource,
              name:'DrawingLayer',
              style: new ol.style.Style({
                fill: new ol.style.Fill({
                  color: 'rgba(255, 255, 255, 0.5)',
                }),
                stroke: new ol.style.Stroke({
                  color: '#ffcc33',
                  width: 2,
                }),
                image: new ol.style.Circle({
                  radius: 7,
                  fill: new  ol.style.Fill({
                    color: '#ffcc33',
                  }),
                }),
              }),
            });
            this.map.addLayer(this.vectorLayer);
        }
    },

    _OnStartDraw : function(e){
        if(e.target.id){
            var self = this;
            this.isDrawingStart=true;
            this.$("#drawingModel").modal('hide');
            this.$("#ol-map-draw-btn").html("<i class='fa fa-play'></i>");
            if (this.map){
                this.modify = new ol.interaction.Modify({
                    source: this.vectorSource,
                    name:'modify',
                });
                this.map.addInteraction(this.modify);
                //var draw, snap;
                var geometryFunction =null;
                if(e.target.id==='Box'){
                    e.target.id='Circle';
                    geometryFunction =new ol.interaction.Draw.createBox();
                }else if(e.target.id === 'Circle'){
                    geometryFunction =new ol.interaction.Draw.createRegularPolygon(32);
                }
                this.draw = new ol.interaction.Draw({
                    source: self.vectorSource,
                    type: e.target.id,
                    geometryFunction:geometryFunction,
                    name:'draw',
                });
                this.map.addInteraction(this.draw);
                this.draw.on('drawend', this._OnDrawEnd.bind(this));
                this.modify.on('modifyend', this._OnDrawEnd.bind(this));

                this.snap = new ol.interaction.Snap({
                        source: this.vectorSource,
                        name:'snap',
                    });
                this.map.addInteraction(this.snap);
            }
        }
    },

    _OnDrawEnd : function(e){
        var self= this;
        setTimeout(function(){
            self.changeGUI();
        }, 100);

    },

    // format data for the current provider
    // response {name,country,state,city,street, postcode}
    _outHtml : function(response){
        var _container = this.$(".o_geocoding_solform");
        _container.empty();
        var html ='';
        _.each(Object.keys(response), function (key) {
            html+='<label class="o_form_label">'+key+': '+response[key]+'</label>';
        });
        _container.append(html);
        this.$(".o_geocoding_solform").show();
    },

    // formatted url return request object {url,method,data,html}
    _formattedUrl : function(provider,service, data){
        return {
            url:this.url[provider]+this.service[provider+'_'+service],
            method:'GET',
            service:service,
            data :data,
        };
    },

    // request object {url,method,data,html}
    _geoCode : function(formatted_request,callback){
        var self = this;
        $.ajax({
            url: formatted_request.url,
            method: 'GET',
            data : formatted_request.data,
            timeout: 1000,
        }).done(function(resp){
            if (formatted_request.service==='reverse'){
                if(resp['features'].length>0){
                    if(resp['features'][0]['properties']){
                        var response=resp['features'][0]['properties']['geocoding'];
                        if(response){
                            var _reverse={
                                label:response['label'],
                                country:response['country'],
                                state:response['state'],
                                street:response['street'],
                                city:response['city'],
                                postcode:response['postcode'],
                            }
                            self._outHtml(_reverse);
                            if(callback){
                                callback(_reverse);
                            }
                        }
                    }
                }
            }else if (formatted_request.service==='search'){
                if(resp['features'].length>0){
                    if(resp['features'][0]['geometry']){
                        var response=resp['features'][0]['geometry']['coordinates'];
                        if(response.length>1){
                            var _search= {
                                lon : response[0],
                                lat : response[1],
                            };
                            self._outHtml(_search);
                            if(callback){
                                callback(_search);
                            }
                        }
                    }
                }
            }
        }).fail(function(resp){
            var _fail = {fail:'fail to load data'};
            self._outHtml(_fail);
        });
    },

    _renderDraggableMarker : function(){
        var self = this;

        var _longitude = this.recordData[this.nodeOptions.longitude];
        var _latitude = this.recordData[this.nodeOptions.latitude];
        if(this.recordData[this.nodeOptions.longitude] === 0.0
               || this.recordData[this.nodeOptions.latitude] === 0.0){
              _longitude= 0.0;
              _latitude= 0.0;
        }
        var coordinates = ol.proj.transform([_longitude,_latitude]
                            ,'EPSG:4326', 'EPSG:3857');
        self.map.getView().setCenter(coordinates);
        setTimeout(function(){
            self.placemark = new ol.Overlay.Placemark({
              position: coordinates,
              stopEvent: false
            });
            self.map.addOverlay(self.placemark);
            if (self.mode==='edit'){
                var drag = new ol.interaction.DragOverlay({
                    overlays: self.placemark
                });
                self.map.addInteraction(drag);
                drag.on('dragend', function(e){
                    var coordinate = ol.proj.transform(e.coordinate
                            ,'EPSG:3857', 'EPSG:4326');
                    if (coordinate.length < 2){
                        return null;
                    }
                    var lat=coordinate[1];
                    var lon=coordinate[0];
                    var url = self._formattedUrl('nominatim','reverse',{
                                lat:lat,
                                lon:lon,
                                format:self.format['nominatim_format']
                            });
                    self._geoCode(url);
                    self.map.getView().setCenter(e.coordinate);
                    self.update_latlng(lat,lon);
                });
            }
         }, 600);
    },

    _on_geCodeButtonClick: function(){
        console.log('geocode_btn',this.nodeOptions.geocode_btn);
        if (this.nodeOptions.geocode_btn){
            if(parseInt(this.nodeOptions.geocode_btn) === 0 ){
                console.log(' return geocode_btn', this.nodeOptions.geocode_btn);
                return;
            }
        }
        var self = this;
        var street,zip,city,state,country ='';
        street = this.recordData[this.nodeOptions.street];
        zip = this.recordData[this.nodeOptions.postalcode];
        city = this.recordData[this.nodeOptions.city];
        state = this.recordData[this.nodeOptions.state];
        country = this.recordData[this.nodeOptions.country];
        // the url should not contain empty value key
        var _data ={};
        if (street){
        _data['street'] = street
        }
        if (zip){
        _data['postalcode'] = zip
        }
        if (city){
        _data['city'] = city
        }
        if(state){
          if(state.data){
              if (state.data.display_name){
                _data['state'] = state.data.display_name
              }
          }
        }
        if (country){
          if(country.data){
              if (country.data.display_name){
                _data['country'] = country.data.display_name
              }
          }
        }
        if (self.format['nominatim_format']){
            _data['format'] = self.format['nominatim_format']
        }
        var url = self._formattedUrl('nominatim','search',_data);
        self._geoCode(url,function(result){
            if(result.lon && result.lat){
                var coordinate = ol.proj.transform([result.lon,result.lat]
                                ,'EPSG:4326', 'EPSG:3857');
                self.map.getView().setCenter(coordinate);
                self.update_latlng(result.lat,result.lon);
                if(!self.placemark){
                    self.placemark = new ol.Overlay.Placemark({
                          position: coordinates,
                          stopEvent: false
                    });
                }else{
                    self.placemark.show(coordinate);
                }
            }
        });
    },

    _renderMap: function (latitude,longitude) {

        if(!latitude){
            latitude = 0;
        }
        if(!longitude){
            longitude = 0;
        }
        if (!this.map) {
              this.map = new ol.Map({
              layers: [
                new ol.layer.Tile({
                  source: new ol.source.OSM(),
                }) ],
              view: new ol.View({
                center: ol.proj.fromLonLat([latitude,longitude]),
                zoom: 13,
              }),
            });
        }
    return this.map;
    },

    changeGUI: function(){
        var valueChange={};
        var _value =  new ol.format.GeoJSON().writeFeatures(this.vectorSource.getFeatures());
        valueChange[this.attrs.name] =_value;
        this.trigger_up("field_changed", {
            dataPointID: this.dataPointID,
            changes: valueChange,
            viewType: this.viewType
        });
        this.value = _value;
    },
    /**
     * @override
     * @private
     */
    _render: function () {
        if(this.map){
            var self= this;
            setTimeout(function(){
                self.map.updateSize();
                self._addTabListener();
            }, 300);
        }
        return $.when();
    },

    update_latlng: function(lat, lng) {
            this.data[this.nodeOptions.latitude]=lat;
            this.data[this.nodeOptions.longitude]=lng;

            var def = $.Deferred();
            var changes = {};
            changes[this.nodeOptions.latitude] = lat;
            changes[this.nodeOptions.longitude] = lng;

            this.trigger_up("field_changed", {
                dataPointID: this.dataPointID,
                changes: changes,
                viewType: this.viewType,
                onSuccess: def.resolve.bind(def),
                onFailure: def.reject.bind(def),
            });
    },

    _createDrawingControl: function () {
        var button = document.createElement('button');
        button.innerHTML = '<i class="fa fa-cube"></i>';
        button.id ='ol-map-draw-btn';
        button.addEventListener('click',this._startDrawingFeatures.bind(this));
        var element = document.createElement('div');
        element.className = 'drawing-control ol-unselectable ol-control';
        element.appendChild(button);
        this.map.addControl(new ol.control.Control({
            element: element
        }));
    },

    _createRemoveControl: function () {
        var button = document.createElement('button');
        button.innerHTML = '<i class="fa fa-trash"></i>';
        button.id ='ol-map-remove-btn';
        button.addEventListener('click',this._startRemoveFeatures.bind(this));
        var element = document.createElement('div');
        element.className = 'remove-control ol-unselectable ol-control';
        element.appendChild(button);
        this.map.addControl(new ol.control.Control({
            element: element
        }));
    },
    _createEditFeaturesControl: function () {
        var button = document.createElement('button');
        button.innerHTML = '<i class="fa fa-pencil"></i>';
        button.id ='ol-map-edit-btn';
        button.addEventListener('click',this._startEditFeatures.bind(this));
        var element = document.createElement('div');
        element.className = 'edit-control ol-unselectable ol-control';
        element.appendChild(button);
        this.map.addControl(new ol.control.Control({
            element: element
        }));

    },
    _startDrawingFeatures: function(){
        if (this.isRemoveStart || this.isEditStart){
            console.log("you can't draw and remove features simultaneity");
            return null;
        }
        if (this.isDrawingStart){
            this.$("#ol-map-draw-btn").html("<i class='fa fa-cube'></i>");
            this.isDrawingStart=false;
            this.map.removeInteraction(this.draw);
            this.map.removeInteraction(this.snap);
            this.map.removeInteraction(this.modify);
        }else{
            this.$("#drawingModel").modal('show');
        }
    },

    _startRemoveFeatures: function(){
        if (this.isDrawingStart || this.isEditStart){
            console.log("you can't draw and remove features simultaneity");
            return null;
        }
        var self = this;
        this.isRemoveStart = !this.isRemoveStart;

        if (this.isRemoveStart){
            this.$("#ol-map-remove-btn").html("<i class='fa fa-play'></i>");
            this.key = this.map.on('singleclick', function(event){
                // remove only the feature in the top
                var isRemoved =false;
                self.map.forEachFeatureAtPixel(event.pixel, function (feature, layer) {
                    if(!isRemoved){
                        self.vectorSource.removeFeature(feature);
                        self.changeGUI();
                    }
                    isRemoved=true;
                });
            });
        }else{
            this.$("#ol-map-remove-btn").html("<i class='fa fa-trash'></i>");
            ol.Observable.unByKey(this.key);
        }
    },
    _startEditFeatures: function(){
        if (this.isDrawingStart || this.isRemoveStart){
            console.log("you can't edit or draw or remove features simultaneity");
            return null;
        }
        var self = this;
        this.isEditStart = !this.isEditStart;
        if (this.isEditStart){
            this.$("#ol-map-edit-btn").html("<i class='fa fa-play'></i>");
            this.key = this.map.on('singleclick', function(event){
                self._SelectedFeature ={};
                // Todo : case : feature in top of another feature
                var isEdit =false;
                self.map.forEachFeatureAtPixel(event.pixel, function (feature, layer) {
                    if(!isEdit){
                        self._SelectedFeature = feature;
                        self._setFormStyleFromFeature(self._SelectedFeature.getProperties());
                        self.$('#EditFeatureModel').modal('show');
                    }
                    isEdit=true;
                });
            });
        }else{
            this.$("#ol-map-edit-btn").html("<i class='fa fa-pencil'></i>");
            ol.Observable.unByKey(this.key);
        }
    },
    _saveEditPropFeature :  function(){
        if (this.isEditStart){
            var featureProp = this._SelectedFeature.getProperties();

            var newProps = this._getFeatureStyleFromGUI();
            this._SelectedFeature.set('fill_color',newProps.fill_color);
            this._SelectedFeature.set('fill_colorHexa',newProps.fill_colorHexa);
            this._SelectedFeature.set('fill_opacity',newProps.fill_opacity);
            this._SelectedFeature.set('stroke_color',newProps.stroke_color);
            this._SelectedFeature.set('stroke_width',newProps.stroke_width);
            this._SelectedFeature.set('image_radius',newProps.image_radius);
            this._SelectedFeature.set('image_fill_color',newProps.image_fill_color);
            this._SelectedFeature.set('key_word',newProps.key_word);
            this._SelectedFeature.setStyle(this._getStyle(newProps));
            this.$('#EditFeatureModel').modal('hide');
            this.changeGUI();
        }
    },
    _closeEditPropFeature :  function(){
        this.$('#EditFeatureModel').modal('hide');
    },

    _closeDrawFeature :  function(){
        this.$('#drawingModel').modal('hide');
    },

    _setFormStyleFromFeature :  function(featureProp){
        this.$("#fill-color").val((featureProp['fill_colorHexa'] ? featureProp['fill_colorHexa']: '#ffcc33'));
        this.$("#fill-opacity").val((featureProp['fill_opacity']?featureProp['fill_opacity'] : 0.2));
        this.$("#stroke-color").val((featureProp['stroke_color']? featureProp['stroke_color']: '#ffcc33'));
        this.$("#stroke-width").val((featureProp['stroke_width']? featureProp['stroke_width']: 2));
        this.$("#image-radius").val((featureProp['image_radius']? featureProp['image_radius']: 7));
        this.$("#image-fill").val((featureProp['image_fill_color']?featureProp['image_fill_color'] : '#ffcc33'));
        this.$("#Key-word").val(featureProp['key_word']);
    },

    _getFeatureStyleFromGUI :  function(){
        var fill_color =this.$("#fill-color").val();
        var fill_colorHexa =this.$("#fill-color").val();
        var fill_opacity =this.$("#fill-opacity").val();
        var stroke_color=this.$("#stroke-color").val();
        var stroke_width=this.$("#stroke-width").val();
        var image_radius=this.$("#image-radius").val();
        var image_fill_color=this.$("#image-fill").val();
        var key_word=this.$("#Key-word").val();

        fill_opacity = (fill_opacity ? fill_opacity : 0.2);
        fill_color = (fill_color ? this.hexToRgbA(fill_color,fill_opacity) : this.hexToRgbA('#ffcc33',fill_opacity));
        stroke_color = (stroke_color ? stroke_color : "#ffcc33");
        stroke_width = (stroke_width ? stroke_width : 2);
        image_radius = (image_radius ? image_radius : 7);
        image_fill_color = (image_fill_color ? image_fill_color : "#ffcc33");

        return {
            fill_color : fill_color,
            fill_colorHexa : fill_colorHexa,
            fill_opacity : fill_opacity,
            stroke_color : stroke_color,
            stroke_width : stroke_width,
            image_fill_color : image_fill_color,
            image_radius : image_radius,
            key_word : key_word,
        };
    },

    _getStyle: function(Props){
        return new ol.style.Style({
            fill: new ol.style.Fill({
              color: Props.fill_color,
            }),
            stroke: new ol.style.Stroke({
              color: Props.stroke_color,
              width: Props.stroke_width,
            }),
            image: new ol.style.Circle({
              radius: Props.image_radius,
              fill: new  ol.style.Fill({
                color: Props.image_fill_color,
              }),
            }),
        });
    },

    _addTabListener: function () {
        if (this.tabListenerInstalled) {
            return;
        }
        var tab = this.$el.closest('div.tab-pane');
        if (!tab.length) {
            return;
        }
        var tab_link = $('a[href="#' + tab[0].id + '"]');
        if (!tab_link.length) {
            return;
        }
        var self  = this;
        tab_link.on('click', function (e) {//shown.bs.tab
            setTimeout(function(){
                self.map.updateSize();
            },300);
        }.bind(this));
        this.tabListenerInstalled = true;
    },

    //https://stackoverflow.com/questions/21646738/convert-hex-to-rgba
    hexToRgbA : function(hex,alpha){
        var r = parseInt(hex.slice(1, 3), 16),
        g = parseInt(hex.slice(3, 5), 16),
        b = parseInt(hex.slice(5, 7), 16);
        return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
    },

});

field_registry.add("solMapForm", MapFormWidget);

return MapFormWidget;

});